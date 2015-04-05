import logging
from django.core.management.base import BaseCommand
from django.db.models import F
from crawl.models import (
    VisaCountry, VisaInformation
)
from crawl.ext.visahq import VisaHq
from celery import task

_logger = logging.getLogger('crawling')

class Command(BaseCommand):
    using_log = True
    logger = None

    def handle(self, *args, **kwargs):
        total_country = VisaCountry.objects.all().count()
        if total_country == 0:
            self.fetch_country()
            total_country = VisaCountry.objects.all().count()

        self.init_logger()

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
                        _send_in_queue.delay(from_country.slug, to_country.slug, from_country.pk, to_country.pk, **kwargs)
                    else:
                        _send_in_queue(from_country.slug, to_country.slug, from_country.pk, to_country.pk, **kwargs)

                from_country.is_running = False
                from_country.save(update_fields=['is_running'])

            is_loop_2nd = True

        res = 200
        return res == 200

    def fetch_country(self):
        self._print('Fetch all Country ...')
        url = 'https://algeria.visahq.co.uk/requirements/United_States/resident-United_Kingdom/'
        country_list = VisaHq.fetch_all_country(url)
        for country in country_list:
            visa_country = VisaCountry(name=country.getText(), slug=country['value'].lower())
            visa_country.save()

    def init_logger(self):
        log_file = '/var/tmp/run_crawlingvisa.log'
        print 'Writing log into file %s ...' % log_file
        self.logger = logging.getLogger('crwalingvisa')

        hdlr = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)

        self.logger.addHandler(hdlr) 
        self.logger.setLevel(logging.WARNING)

    def _print(self, s):
        if self.using_log:
            self.logger.info(s)
        else:
            print s.encode('utf-8')


@task
def _send_in_queue(from_name, to_name, from_id, to_id, **param):

    BASE_DOMAIN = 'https://%s.visahq.com/requirements/%s/resident-%s/'

    base_url = BASE_DOMAIN % (to_name, from_name, from_name)
    business_url = base_url + '#!%s-business-visa' % to_name

    print 'Crawling data from %s to %s' % (from_name, to_name)

    visa_information = VisaHq.fetch_all_visa_information(base_url, business_url)
    if visa_information:
        tourist_visa = visa_information['tourist_visa']
        business_visa = visa_information['business_visa']
        details_tourist = visa_information['details_tourist']
        details_business = visa_information['details_business']

        visa_info = VisaInformation.objects.create(
            from_country_id=from_id, to_country_id=to_id, tourist_visa=tourist_visa,
            business_visa=business_visa, details_tourist=details_tourist,
            details_business=details_business
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