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

class BookingCrawler(BaseCrawler):

    def __init__(self, site_base_url, mongodb):
        self.site_base_url = site_base_url
        self.logger = setuplogger(loggername='booking_crawler')
        self.driver = None
        self.hotels_per_page =15
        self.db = mongodb

    def __del__(self):
        # self.driver.quit().
        pass

    # returns list of URLs of all hotels to parse
    # expected contents of meta_dict:
    #  - full_name (of city)
    #  - city_ID (tripadvisor)
    #  - country (name)
    def crawl_hotels(self, base_url, metadata_dict={}):
        hotel_dict_list = []
        hotel_limit = -1
        page_count = 1
        tries = 0
        max_tries = 3
        search_url = base_url

        while True:
            try:
                soup = BeautifulSoup(
                    requests.get(search_url).text)
            except:
                self.logger.info("cannot retrieve page - exiting")
                break

            self.logger.info("parsing list of hotels from {0}".format(search_url))

            for listing in soup.find(id="hotellist_inner").findAll("div", "sr_item clearfix"):
                try:
                    url = self.site_base_url + listing.find("h3").find("a")['href'].split("?")[0]
                    hotel_id = listing["data-hotelid"]
                    hotel_dict_list.append({
                        "url": url,
                        "hotel_id": hotel_id,
                        "source": "Booking"
                    })
                except:
                    self.logger.info("No url present in listing {0}".format(listing))

            # look for next page url
            if soup.find("a", "paging-next"):
                search_url = soup.find("a", "paging-next")['href']
            else:
                break

        self.logger.info("hotel url list has {0} entries".format(len(hotel_dict_list)))
        return hotel_dict_list


    def get_hotels(self, base_url, metadata_dict={}):
        if self.db.hotel_url.find({'source': 'Booking'}).count() == 0:
            hotel_dict_list = self.crawl_hotels(base_url, metadata_dict)
            for item in hotel_dict_list:
                self.db.hotel_url.insert(item)
        return list(self.db.hotel_url.find(
            {'source': 'Booking'},
            {'url': 1, 'hotel_id': 1}))

    # we will use json to crawl the reviews.
    # :return - max int - page number
    def crawl_reviews(self, base_url, metadata_dict):
        return None
