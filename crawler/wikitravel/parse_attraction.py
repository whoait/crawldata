__author__ = 'ongzhongliang'

from BeautifulSoup import BeautifulSoup
from selenium import webdriver
from ..string_util import setuplogger
from ..base.parse_hotel import BaseHotel


class WikitravelAttraction(BaseHotel):
    def __init__(self, driver, base_url, soup):
        super(WikitravelAttraction, self).__init__(driver, base_url)
        self.driver = driver
        self.attraction_soup = soup
        self.url = base_url
        self.logger = setuplogger(loggername='wikitravel_attraction')

    def parse_name(self):
        name_soup = self.attraction_soup.find("span", "fn org")
        return name_soup.text or None

    def get_site_id(self):
        return self.url + '#' + self.attraction_soup['id']

    def parse_source_entity_id(self):
        return self.get_site_id()

    def parse_source(self):
        return "Wikitravel"

    def parse_address(self):
        address_soup = self.attraction_soup.find("span", "adr")
        return address_soup.text if address_soup else None

    def parse_postcode(self):
        return None

    def parse_lat(self):
        return None

    def parse_lng(self):
        return None

    def parse_city(self):
        # should be passed directly to hotel as arg
        raise NotImplementedError()

    def parse_country(self):
        # should be passed directly to hotel as arg
        raise NotImplementedError()

    def parse_category(self):
        edit_soup = self.attraction_soup.find("a", "listing-edit")
        if edit_soup and edit_soup.get("onclick"):
            try:
                param_list = edit_soup.get("onclick").split("(")[1].split(',')
                if len(param_list) > 2:
                    return param_list[1]
            except AttributeError:
                self.logger.info("attribute error for {0}".format(edit_soup))
                pass
            except IndexError:
                self.logger.info("index error for {0}".format(edit_soup))
                pass
        return None

    def parse_website(self):
        web_soup = self.attraction_soup.find("a", "url")
        return web_soup.get('href') if web_soup else None

    def parse_phone(self):
        phone_soup = self.attraction_soup.find("span", "phone")
        return phone_soup.text if phone_soup else None

    def parse_email(self):
        email_soup = self.attraction_soup.find("span", "email")
        return email_soup.text if email_soup else None

    def parse_description(self):
        desc_soup = self.attraction_soup.find("span", "description")
        return desc_soup.text if desc_soup else None

    def parse_short_description(self):
        pass

    def parse_avatar(self):
        return None

    def parse_entity_source_rating(self):
        return {}

    def parse_prices(self):
        price_soup = self.attraction_soup.find("span", "price")
        return {'price_text': price_soup.text} if price_soup else {}

    def parse_open_time(self):
        open_soup = self.attraction_soup.find("span", "hours")
        return {'opening_text': open_soup.text} if open_soup else {}
