import re
import urllib2
import httplib
from urllib2 import HTTPError
import logging

from BeautifulSoup import BeautifulSoup as Soup

_logger = logging.getLogger('crawling')


class RoundRobinProxySelector:
    index = 0
    num_proxies = 0
    proxies = []
    def __init__(self, proxies=[]):
        self.proxies = proxies
        self.num_proxies = len(proxies)

    def get_proxy(self):
        if not self.proxies:
            return None
        else:
            proxy = self.proxies[self.index]
            self.index = (self.index + 1) % self.num_proxies
            print '<*> Using proxy %s' % proxy[1]
            return proxy


LIST_PROXIES = [
    ('http', '88.150.136.178:3129'),
    ('http', '88.150.136.179:3129'),
    ('http', '88.150.136.180:3128'),
    ('http', '88.150.136.181:3128'),
]
proxy_selector = RoundRobinProxySelector(LIST_PROXIES)


class VisaHq:

    @classmethod
    def fetch_all_visa_information(cls, base_url, business_url):
        if base_url:
            try:
                status, html = VisaHq.fetch_html(base_url)
                business_status, business_html = VisaHq.fetch_html(business_url)
            except Exception as e:
                _logger.info('Unexpected errors %s ' % e)

            if status == 200 and business_status == 200:
                info_list = VisaHq.parse_visa_information_html(html, business_html)
                return info_list
        return None

    @classmethod
    def fetch_all_country(cls, url):
        if url:
            status, html = VisaHq.fetch_html(url)
            if status == 200:
                option_list = VisaHq.parse_country_html(html)

                return option_list
        return None

    @classmethod
    def fetch_html(cls, url, headers=None, use_proxy=True):
        status = 200
        html = None
        msg = None
        req = None

        if not use_proxy:
            if headers:
                req = urllib2.Request(url, headers=headers)
            else:
                req = urllib2.Request(url)
        else:
            proxy_config = proxy_selector.get_proxy()
            proxy = urllib2.ProxyHandler({proxy_config[0]: proxy_config[1]})
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)
            req = url

        try:
            response = urllib2.urlopen(req)
        except HTTPError as e:
            status = e.code
            msg = e.msg
            try:
                html = e.read()
            except Exception:
                html = None
        except urllib2.URLError as e1:
            print e1.__dict__
        except httplib.BadStatusLine as e:
            print e.__dict__
        else:
            try:
                html = response.read()
            except httplib.IncompleteRead, e:
                html = e.partial
            status = response.code

        print 'REQUEST', url, headers, status
        return status, html

    @classmethod
    def parse_country_html(cls, html):
        if html:
            soup = Soup(html)

            els_name = soup.find('select', attrs={'id': re.compile(r'.*\bctz\b.*')})
            option_list = els_name.findAllNext('option')

            return option_list
        return None

    @classmethod
    def parse_visa_information_html(cls, html, business_html):
        if html and business_html:
            soup = Soup(html)
            business_soup = Soup(business_html)

            els_tourist_name = soup.find('dl', attrs={'id': re.compile(r'.*\bvisa_group_1\b.*')})
            els_business_name = soup.find('dl', attrs={'id': re.compile(r'.*\bvisa_group_2\b.*')})
            els_tourist_visa_info = soup.find('div', attrs={'class': re.compile(r'.*\bvisa_info_data\b.*')})
            els_business_visa_info = business_soup.find('div', attrs={'class': re.compile(r'.*\bvisa_info_data\b.*')})

            if 'not required' in els_tourist_name['class']:
                tourist_required = False
            else:
                tourist_required = True

            if 'not required' in els_business_name['class']:
                business_required = False
            else:
                business_required = True

            return {
                'tourist_visa'      : tourist_required,
                'business_visa'     : business_required,
                'details_tourist'   : str(els_tourist_visa_info),
                'details_business'  : str(els_business_visa_info),
            }

        return None

def main():
    test_exclude = [255117070, 254476771, 250948641]
    test_url = 'https://algeria.visahq.co.uk/requirements/United_States/resident-United_Kingdom/'
    test_url2 = 'https://cambodia.visahq.com/requirements/Vietnam/resident-VietNam/'

    test_url3 = 'https://cambodia.visahq.com/requirements/Vietnam/resident-VietNam/#!cambodia-business-visa'

    visa_infomation = VisaHq.fetch_all_visa_information(test_url2, test_url3)

    print visa_infomation



if __name__ == "__main__":
    main()
