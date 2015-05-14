"""
Base Crawler Rules
Rules help the crawler locate links in webpages
"""
from ..string_util import setuplogger

class BaseCrawler(object):
    # Base URL allows using JSON feeds instead of HTML if available
    def __init__(self, site_base_url):
        self.logger = setuplogger(loggername="Crawler")

    # returns URLs of all hotels to crawl
    # base_url corresponds to the first page of hotel listings in a city
    def crawl_hotels(self, base_url, metadata_dict={}):
        raise NotImplementedError()

    # returns URLs of all reviews to crawl
    # base_url corresponds to the first page of reviews for a hotel
    def crawl_reviews(self, base_url, metadata_dict={}):
        raise NotImplementedError()
