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

class VirtualtouristCrawler(BaseCrawler):

    def __init__(self, site_base_url, mongodb):
        self.site_base_url = site_base_url
        self.logger = setuplogger(loggername='virtualtourist_crawler')
        self.driver = None
        self.hotels_per_page = 25
        self.db = mongodb

    def __del__(self):
        # self.driver.quit().
        pass

    def extract_data_from_soup(self, item_soup):
        try:
            url = item_soup.find("a").get('href')
            if not url:
                raise Exception("No data")

            hotel_id = item_soup["data-id"]

            review_count_soup = item_soup.find("div", "hotel-rating")
            review_count = 0
            if review_count_soup and review_count_soup.text:
                review_count_buf = review_count_soup.text.split(' ')[0]
                if len(review_count_buf) > 0:
                    review_count = int(review_count_buf)

            rating = 0
            rating_soup = item_soup.find("div", "usr-rating")
            if rating_soup:
                attrs_list = rating_soup.attrs
                for rating_tuple in attrs_list:
                    if rating_tuple[0] == 'class':
                        for usr_rating_string in rating_tuple[1].split(' '):
                            if usr_rating_string != 'usr-rating':
                                try:
                                    rating = float(usr_rating_string.split('usr-rating-')[1])/10
                                except ValueError:
                                    self.logger.info("No value could be parsed from {0}".format(usr_rating_string))

            stars = 0
            star_soup = item_soup.find("div", "hotel-class-wrap")
            if star_soup:
                if star_soup.find("div", "hotel-class-grey"):
                    stars = len(star_soup.find("div", "hotel-class-grey").findAll('span'))

            lat_soup = item_soup.find(itemprop="latitude")
            lat = float(lat_soup.get('content')) if lat_soup else None

            lng_soup = item_soup.find(itemprop="longitude")
            lng = float(lng_soup.get('content')) if lng_soup else None

            return ({
                "url": url,
                "review_count": review_count,
                "rating": rating,
                "stars": stars,
                "lat": lat,
                "lng": lng,
                "hotel_id": hotel_id,
                "source": "Virtualtourist",
            })

        except Exception, err:
            import traceback
            import sys
            self.logger.info(traceback.format_exc())
            self.logger.info("No url present in listing {0}".format(item_soup))
            return None

    # returns list of URLs  of all hotels to parse
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

            for listing in soup.find(id="hotelListItems").findAll("li"):
                if listing.get('data-id'):
                    try:
                        hotel_dict_list.append(self.extract_data_from_soup(listing))
                    except:
                        self.logger.info("No url present in listing {0}".format(listing))

            # look for next page url
            if soup.find("li", "page-next"):
                search_url = soup.find("li", "page-next").find("a")['href']
            else:
                break

        self.logger.info("hotel url list has {0} entries".format(len(hotel_dict_list)))
        return hotel_dict_list

    # we will use json to crawl the reviews.
    # :return - max int - page number
    def crawl_reviews(self, base_url, metadata_dict):
        return_list = []
        for i in xrange(1, metadata_dict['review_count']+1):
            return_list.append(
                base_url.replace('-BR-1.html', '-BR-{0}.html'.format(i))
            )
        return return_list
