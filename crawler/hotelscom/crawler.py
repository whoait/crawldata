"""
Base Crawler Rules
Rules help the crawler locate links in webpages
"""
import sys
import os
from datetime import datetime, timedelta
from selenium import webdriver
from BeautifulSoup import BeautifulSoup
import urllib2
import requests
import json

from ..base.crawler import BaseCrawler
from ..string_util import setuplogger

class HotelscomCrawler(BaseCrawler):

    def __init__(self, site_base_url):
        self.site_base_url = site_base_url
        self.logger = setuplogger(loggername='hotelscom_crawler')
        self.driver = webdriver.Firefox()

    def __del__(self):
        self.driver.quit()

    # returns list of URLs of all hotels to parse
    # expected contents of meta_dict:
    #  - full_name (of city)
    #  - city_ID (tripadvisor)
    #  - country (name)
    def crawl_hotels(self, base_url, metadata_dict={}):
        hotel_url_list = []

        # we need to find the Hotels.com API page
        city_url = "{0}/search/listings.json?".format(
            self.site_base_url
        )

        # Need to generate dummy time
        time_now = datetime.now()
        time_checkin = time_now + timedelta(days=30)
        time_checkout = time_now + timedelta(days=32)
        string_checkout = time_checkout.strftime("%d/%m/%Y")
        string_checkin = time_checkin.strftime("%d/%m/%Y")

        # we'll construct the URL for tripadvisor ourselves
        url_options_dict = {
            'q-localised-check-out': string_checkout,
            'q-localised-check-in': string_checkin,
            'q-room-0-adults': 2,
            'destination-id': metadata_dict['cityID'],
            'q-destination': "Singapore,+Singapore",
            'q-room-0-children': 0,
            'pn': 1,
            'q-rooms': 1,
            'start-index': 0,
            'resolved_location': "CITY:{0}:PROVIDED:PROVIDED".format(
                metadata_dict["cityID"]
            )
        }
        for option in url_options_dict:
            city_url += option + "=" + str(url_options_dict[option]) + "&"
        self.driver.get(city_url)
        raw_json = self.driver.find_element_by_tag_name("body").text
        self.logger.info("trying url = {0}".format(city_url))
        json_pages = json.loads(raw_json)

        results_dict = json_pages.get("data").get("body").get("searchResults")
        self.logger.info("keys in result set = {0}".format(results_dict.keys()))
        results_list = results_dict.get("results")

        added_count = 0
        total_count = results_dict.get("totalCount")
        self.logger.info("total count = {0}, results_list length = {1}".format(
            total_count, len(results_list)))

        while added_count < total_count:
            for hotel in results_list:
                hotel_url_list.append(self.site_base_url +
                                      hotel.get("urls").get("pdpDescription"))
                added_count += 1
            self.logger.info("Finished scanning current page - {0} added - total = {1}".format(
                added_count, total_count
            ))

            # getting next page url (if it exists)
            next_page_param = results_dict.get("pagination").get("nextPageUrl")
            self.logger.info("next page param = {0}".format(next_page_param))

            url_options_dict['pn'] += 1
            url_options_dict['start-index'] += 50 if added_count <= 50 else 20
            next_page_url = "{0}/search/listings.json?".format(
                self.site_base_url
            )
            for option in url_options_dict:
                next_page_url += option + "=" + str(url_options_dict[option]) + "&"

            # load next page
            try:
                if next_page_url:
                    # params given in next_page_url
                    self.logger.info("next page url = {0}".format(next_page_url))
                    self.driver.get(next_page_url)
                    raw_json = self.driver.find_element_by_tag_name("body").text
                    json_pages = json.loads(raw_json)
                    results_dict = json_pages.get("data").get("body").get("searchResults")
                    results_list = results_dict.get("results")
                    self.logger.info("total count = {0}, results_list length = {1}".format(
                        total_count, len(results_list)))
                # load next page
            except:
                break

        return hotel_url_list

    # returns list of review URLs to parse
    # expected contents of metadata_dict
    # - nothing we'll split the base URL
    def crawl_reviews(self, base_url, metadata_dict):
        review_url_list = []

        # we're using the base_url
        # we only have 5 entries on the list - but each entry has 50 reviews
        # we are only able to get up to 250 reviews {1-5 stars -
        # each having up to 50 reviews }, because hotels.com doesn't show all

        review_base_url = "{0}/hotel/{1}/reviews/".format(
            self.site_base_url,
            metadata_dict['hotel_id']
        )

        review_base_params = {}

        for review_score in xrange(1, 5):
            review_base_params['reviewOrder'] = 'date_newest_first'
            review_base_params['scoreFilter'] = review_score

            review_url_list.append(
                requests.get(review_base_url, params=review_base_params).url
            )

        return review_url_list
