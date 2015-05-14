"""
Parser functions
"""
from BeautifulSoup import BeautifulSoup, NavigableString, Tag
from selenium import webdriver
import datetime
import re
import urllib2
import traceback

from ..base.parse_review import BaseReview
from ..string_util import filter_description, strip_punctuation_whitespace


class VirtualtouristReview(BaseReview):

    def __init__(self, driver, base_url, soup, entity_source_id):
        super(VirtualtouristReview, self).__init__(driver, base_url)
        # reviews extracted via json

        self.soup = soup

        ## try using urllib2 here:
        # NO URLLIB - it defaults to ascii
        #self.soup = BeautifulSoup(
        #	urllib2.urlopen(self.base_url).read())
        # initialized commonly reused fields

        self.entity_source_id = entity_source_id
        self.detail_dict = self.parse_details()
        self.categories = [
                            'Family',
                            'Couple',
                            'Group of friends',
                            'Solo traveler',
                            'Leisure trip',
                            'Business trip',
                            'Traveler with pets'
                            ]

    def parse_source(self):
        return "Virtualtourist"

    def parse_title(self):
        return self.soup.find(itemprop="name").text

    def parse_details(self):
        detail_dict = {}
        detail_soup = self.soup.find("div", "written-by")
        if detail_soup:
            url = detail_soup.find(itemprop="author").get('href')
            if url:
                detail_dict['site_id'] = url.split("/p/m/")[1].split("/")[0]
                detail_dict['username'] = detail_soup.text
            if 'written on ' in detail_soup.text:
                date_string = detail_soup.text.split('written on ')[1]
                detail_dict['date'] = datetime.datetime.strptime(
                    date_string,
                    "%B %d, %Y")
        return detail_dict

    def parse_site_id(self):
        return self.detail_dict.get('site_id')

    def parse_username(self):
        return self.detail_dict.get('username')

    def parse_user_id(self):
        # we cannot retrive a userID from Booking.com
        member_soup = self.soup.find("img", "img-circle")
        if member_soup:
            return member_soup.get("data-memberid")
        return None

    def parse_place_from(self):
        return None

    def parse_helpful(self):
        return None

    def parse_date(self):
        return self.detail_dict.get("date")

    def parse_review_text(self):
        # Booking.com only has pos/neg reviews
        return filter_description(
            unicode(
                self.soup.find(
                    itemprop="description")))

    def parse_review_positive(self):
        return None

    def parse_review_negative(self):
        return None

    def parse_entity_source_id(self):
        return self.entity_source_id

    def parse_review_categories(self):
        category_list = []
        return category_list

    def parse_review_rating(self):
        rating_dict = {}
        rating_soup = self.soup.find(itemprop="ratingValue")
        if rating_soup:
            try:
                rating_dict['overall'] = float(rating_soup.get('content')) * 100 / 5
            except:
                self.logger.info("cannot parse float for soup = {0}".format(rating_soup))

        #self.logger.info("extracted rating dict =  {0} for review {1}".format(
        #    rating_dict,
        #    self.parse_title()))

        return rating_dict
