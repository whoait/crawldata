"""
Base Crawler Rules
Rules help the crawler locate links in webpages
"""
import sys
import os
import urllib2
from BeautifulSoup import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


from ..base.crawler import BaseCrawler
from ..string_util import setuplogger
from .util import binary_search_url


class AgodaCrawler(BaseCrawler):

    def __init__(self, site_base_url):
        self.site_base_url = site_base_url
        self.logger = setuplogger(loggername='agoda_crawler')
        self.driver = webdriver.Firefox()

    # returns list of URLs of all hotels to parse
    # expected contents of meta_dict:
    #  - full_name (of city)
    #  - city ID (Agoda)
    #  - country (name)
    def crawl_hotels(self, base_url, metadata_dict={}):
        hotel_url_list = []
        # we'll construct the URL for tripadvisor ourselves
        self.driver.get(base_url)

        added_count = 0

        while True:
            list_soup = BeautifulSoup(
                self.driver.page_source)
            # exit via break
            hotel_list_soup = (list_soup.
                               find(id="result-wrapper").
                               find("ol"))
            if hotel_list_soup:
                hotel_url_list_soup = list(hotel_list_soup.findAll("li"))
                for hotel_url in hotel_url_list_soup:
                    if hotel_url.has_key("data-hotel-url"):
                        hotel_url_list.append("http://www.agoda.com" + hotel_url['data-hotel-url'].split("?")[0])
                        added_count += 1

            try:
                click_target = self.driver.find_element_by_xpath("//a[@name='pageNext']")
            except NoSuchElementException:
                self.logger.info("reached end of list - have {0} hotels".format(added_count))
                break

            actions = ActionChains(self.driver)
            actions.move_to_element(click_target)
            actions.click()
            actions.perform()

        return hotel_url_list

    # returns list of review URLs to parse
    # expected contents of metadata_dict
    # - nothing we'll split the base URL
    def crawl_reviews(self, base_url, metadata_dict):

        # we're using the requests module as the webdriver doesn't
        # report HTTP response codes - we want to iterate through page IDs
        # until we run out of response codes

        added_count = 0
        page_count = 1
        max_tries = 3

        review_url_list = binary_search_url(base_url)
        self.logger.info("review_url_list size = {0}".format(review_url_list))
        return review_url_list
