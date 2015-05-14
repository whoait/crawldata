"""
Parser functions
"""
from BeautifulSoup import BeautifulSoup
from selenium import webdriver

from ..string_util import setuplogger


class BaseReview(object):

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.logger = setuplogger(loggername='Parse Review')

    def parse_source(self):
        raise NotImplementedError()

    def parse_title(self):
        raise NotImplementedError()

    def parse_user_id(self):
        raise NotImplementedError()

    def parse_site_id(self):
        raise NotImplementedError()

    def parse_username(self):
        raise NotImplementedError()

    def parse_place_from(self):
        raise NotImplementedError()

    def parse_helpful(self):
        raise NotImplementedError()

    def parse_date(self):
        raise NotImplementedError()

    def parse_review_text(self):
        raise NotImplementedError()

    def parse_review_positive(self):
        raise NotImplementedError()

    def parse_review_negative(self):
        raise NotImplementedError()

    def parse_entity_source_id(self):
        raise NotImplementedError()

    def parse_review_rating(self):
        raise NotImplementedError()

    def parse_review_categories(self):
        raise NotImplementedError()