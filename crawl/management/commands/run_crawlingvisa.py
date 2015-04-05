import logging
import unidecode
import re
from django.core.management.base import BaseCommand
from django.db.models import F
from crawl.models import (
    VisaCountry, VisaInformation
)

from crawl.ext.visahq import VisaHq
from celery import task

_SLUGIFY_RE = re.compile(r'\W+', re.I)
_logger = logging.getLogger('commands')

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        total_country = VisaCountry.objects.all().count()

        if total_country == 0:
            self.fetch_country()
            total_country = VisaCountry.objects.all().count()

        is_loop_2nd = False
        while True:
            country_list = VisaCountry.objects.filter(is_running=0)\
                .exclude(total_completed=total_country)\
                .order_by('id')

            if not country_list:
                break

            delay = kwargs.get('delay')

            for from_country in country_list:

                if is_loop_2nd:
                    remained_country = from_country.get_remained_to_country()
                else:
                    remained_country = country_list

                stop_at = from_country.stop_at
                if not stop_at:
                    stop_at = 0

                for to_country in remained_country:
                    if to_country.pk == from_country.pk or to_country.pk <= int(stop_at):
                        continue

                    if delay:
                        _send_in_queue.delay(from_country.code, to_country.code, from_country.pk, to_country.pk, **kwargs)
                    else:
                        _send_in_queue(from_country.code, to_country.code, from_country.pk, to_country.pk, **kwargs)

                from_country.is_running = False
                from_country.save(update_fields=['is_running'])

            is_loop_2nd = True

        res = 200
        return res == 200

    def slugify(self, s):
        s = unidecode.unidecode(s.strip())
        slug = _SLUGIFY_RE.sub('-', s).strip('-').lower()

        return slug

    def fetch_country(self):
        print 'Fetch all Country ...'
        # url = 'https://algeria.visahq.co.uk/requirements/United_States/resident-United_Kingdom/'
        url = 'https://www.visahq.com/get_widget.php'
        country_list = VisaHq.fetch_all_country(url)

        for country in country_list:
            if country['value'] != "0":
                name = country.getText()
                visa_country = VisaCountry(name=name, code=country['value'], slug=self.slugify(name))
                visa_country.save()

# def init_logger():
#     log_file = '/var/tmp/run_crawlingvisa.log'
#     print 'Writing log into file %s ...' % log_file
#     _logger = logging.getLogger('crwalingvisa')
#
#     hdlr = logging.FileHandler(log_file)
#     formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
#     hdlr.setFormatter(formatter)
#
#     _logger.addHandler(hdlr)
#     _logger.setLevel(logging.WARNING)


@task
def _send_in_queue(from_name, to_name, from_id, to_id, **param):

    BASE_DOMAIN = 'https://%s.visahq.com/requirements/%s/resident-%s/'
    BASE_WIDGET = 'https://www.visahq.com/widget_6.php?citizen=%s&dest=%s&lang=us&resid=US&type=flash_java&view=Flash&pln=&is_click=1&visa_type=%s'
    # base_url = BASE_DOMAIN % (to_name, from_name, from_name)
    # business_url = base_url + '#!%s-business-visa' % to_name
    base_url = BASE_WIDGET % (from_name, to_name, 'tourist')
    business_url = BASE_WIDGET % (from_name, to_name, 'business')

    print 'Crawling data from %s to %s' % (from_name, to_name)
    visa_information = VisaHq.fetch_all_visa_information(base_url, business_url)

    if visa_information:
        tourist_visa = visa_information['tourist_visa']
        business_visa = visa_information['business_visa']
        # details_tourist = visa_information['details_tourist']
        # details_business = visa_information['details_business']

        visa_info = VisaInformation.objects.create(
            from_country_id=from_id, to_country_id=to_id,
            tourist_visa=tourist_visa, business_visa=business_visa
        )
        try:
            visa_info.full_clean()
        except Exception as e:
            _logger.info('Data errors %s' % e)
        else:
            visa_info.save()
            from_country = VisaCountry.objects.get(pk=from_id)
            from_country.refresh()
            from_country.is_running = True
            from_country.stop_at = to_id
            from_country.save(update_fields=['is_running', 'stop_at'])

            if from_country.is_completed():
                from_country.is_running = False
                from_country.save(update_fields=['is_running'])

        _logger.info('SUCCESS Crawling data from %s to %s' % (from_id, to_id))
    else:
        _logger.info('No Visa information data from %s to %s' % (from_id, to_id))