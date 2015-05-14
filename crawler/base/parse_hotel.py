"""
Parser functions
"""
from BeautifulSoup import BeautifulSoup
from selenium import webdriver

from ..string_util import setuplogger


class BaseHotel(object):
    # BaseHotel receives soup for hotel listing
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.logger = setuplogger(loggername='Parse Hotel')

    def parse_name(self):
        raise NotImplementedError()

    def parse_source_entity_id(self):
        raise NotImplementedError()

    def parse_source(self):
        raise NotImplementedError()

    def parse_address(self):
        raise NotImplementedError()

    def parse_postcode(self):
        raise NotImplementedError()

    def parse_lat(self):
        raise NotImplementedError()

    def parse_lng(self):
        raise NotImplementedError()

    def parse_city(self):
        raise NotImplementedError()

    def parse_country(self):
        raise NotImplementedError()

    def parse_category(self):
        raise NotImplementedError()

    def parse_email(self):
        raise NotImplementedError()

    def parse_website(self):
        raise NotImplementedError()

    def parse_phone(self):
        raise NotImplementedError()

    def parse_description(self):
        raise NotImplementedError()

    def parse_avatar(self):
        raise NotImplementedError()

    def parse_entity_source_rating(self):
        raise NotImplementedError()

    def parse_all_photos(self):
        raise NotImplementedError()

    def parse_amenity(self):
        raise NotImplementedError()
