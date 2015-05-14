"""
Base Crawler Rules
Rules help the crawler locate links in webpages
"""
import time
from datetime import datetime, timedelta
from selenium import webdriver
from BeautifulSoup import BeautifulSoup
import urllib2
import requests
import json

from ..base.crawler import BaseCrawler
from ..string_util import setuplogger

class ExpediaCrawler(BaseCrawler):

    def __init__(self, site_base_url):
        self.site_base_url = site_base_url
        self.logger = setuplogger(loggername='expedia_crawler')
        self.driver = webdriver.Firefox()
        self.hotels_per_page = 50

    def __del__(self):
        self.driver.quit()

    # returns list of URLs of all hotels to parse
    # expected contents of meta_dict:
    #  - full_name (of city)
    #  - city_ID (tripadvisor)
    #  - country (name)
    def crawl_hotels(self, base_url, metadata_dict={}):
        hotel_url_list = []
        hotel_limit = -1
        page_count = 1
        tries = 0
        max_tries = 3
        while True:
            search_url = base_url + "&page={0}".format(page_count)
            try:
                self.driver.get(search_url)
                soup = BeautifulSoup(self.driver.page_source)
            except:
                self.logger.info("cannot retrieve page - exiting")
                break

            if hotel_limit == -1:
                while tries < max_tries:
                    limit_text = soup.find("h1", "section-header-main").text
                    try:
                        hotel_limit = int(limit_text.split(' hotels in')[0])
                        tries = 0
                        break
                    except:
                        self.logger.info("cannot retrieve hotel limit from {0} in {1}".
                            format(limit_text, search_url))
                        if tries < max_tries:
                            tries += 1
                            time.sleep(5)
                            soup = BeautifulSoup(self.driver.page_source)
                            continue
                self.logger.info("limit = {0}".format(hotel_limit))

            raw_hotel_url_list = soup.findAll("div", "hotelWrapper")
            if raw_hotel_url_list:
                if len(raw_hotel_url_list) == 0:
                    break
                self.logger.info("saw {0} hotels for url = {1}".format(
                    len(raw_hotel_url_list), search_url))
                for hotel in raw_hotel_url_list:
                    url_str = hotel.find("a")["href"]
                    if url_str:
                        if url_str.startswith("http://www.expedia.com"):
                            hotel_url_list.append(url_str)
            page_count += 1
            if (page_count - 1)* self.hotels_per_page > hotel_limit:
                break

        self.logger.info("hotel url list has {0} entries".format(len(hotel_url_list)))
        return hotel_url_list

    # we will use json to crawl the reviews.
    # :return - max int - page number
    def crawl_reviews(self, base_url, metadata_dict):
        soup = BeautifulSoup(urllib2.urlopen(base_url).read())
        try:
            return int(soup.find(itemprop="reviewCount").text)
        except:
            return None
