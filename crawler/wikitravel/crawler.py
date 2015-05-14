__author__ = 'ongzhongliang'

from BeautifulSoup import BeautifulSoup
import urllib2
import requests
import json
from selenium import webdriver

from ..base.crawler import BaseCrawler
from ..string_util import setuplogger

class WikitravelCrawler(BaseCrawler):

    def __init__(self, site_base_url, mongodb):
        self.site_base_url = site_base_url
        self.logger = setuplogger(loggername='wikitravel_crawler')
        self.driver = webdriver.Firefox()
        self.hotels_per_page = 25
        self.db = mongodb

    def __del__(self):
        # self.driver.quit().
        pass

    def crawl_attractions(self, base_url, metadata_dict={}):
        self.driver.get(base_url)
        return [href.get_attribute('href')
                for href in
                self.driver.find_elements_by_xpath("//ul/li/b/a")]

    def crawl_reviews(self, base_url, metadata_dict):
        pass
