"""
Parser functions
"""
from BeautifulSoup import BeautifulSoup, NavigableString, Tag
from selenium import webdriver
import datetime
import urllib2
import traceback

from ..base.parse_review import BaseReview
from ..string_util import strip_punctuation_whitespace


class ExpediaReview(BaseReview):

    def __init__(self, driver, base_url, soup, json_dict):
        super(ExpediaReview, self).__init__(driver, base_url)
        # reviews extracted via json

        self.soup = None
        self.dict = json_dict

        ## try using urllib2 here:
        # NO URLLIB - it defaults to ascii
        #self.soup = BeautifulSoup(
        #	urllib2.urlopen(self.base_url).read())
        # initialized commonly reused fields


        try:
            self.entity_source_id = int(
                self.dict.get('hotelId'))
        except:
            self.entity_source_id = 0
            self.logger.info(
                "cannot assign entity_source_id to url = {0}".
                format(self.dict))
        # review_soup
        self.rating_translation_table = {
            "ratingHotelCondition"      : "Facility",
            "ratingRoomComfort"         : "Room",
            "ratingRoomCleanliness"     : "Cleanliness",
            "ratingService"             : "Service"
        }


    def parse_source(self):
        return "Expedia"

    def parse_title(self):
        return self.dict.get('title')

    def parse_site_id(self):
        return self.dict.get('reviewId')

    def parse_username(self):
        return self.dict.get('userNickname')

    def parse_user_id(self):
        # we cannot retrive a userID from expedia
        """
        if self.member_soup:
            screenname_soup = self.member_soup.find(
                "span", "scrname")
            if screenname_soup:
                class_soup = screenname_soup.get('class')
                class_list = []
                if class_soup:
                    class_list = class_soup.split(' ')
                for attr in class_list:
                    if attr.startswith("mbrName_"):
                        return attr.split("mbrName_")[1]
        """
        return None

    def parse_place_from(self):
        return self.dict.get('userLocation')

    def parse_helpful(self):
        return self.dict.get('totalThanks')

    def parse_date(self):
        date_string = self.dict.get('reviewSubmissionTime')
        if date_string:
            return datetime.datetime.strptime(
                date_string,
                "%Y-%m-%dT%H:%M:%SZ")
        return None

    def parse_review_text(self):
        return self.dict.get("reviewText")

    def parse_review_positive(self):
        return self.dict.get('positiveRemarks')

    def parse_review_negative(self):
        return self.dict.get('negativeRemarks')

    def parse_entity_source_id(self):
        return self.entity_source_id

    def parse_review_rating(self):
        rating_dict = {}
        rating_dict['overall'] = self.dict.get('ratingOverall') * 100 / 5
        for item in self.rating_translation_table:
            rating_dict[self.rating_translation_table[item]] = self.dict[item] * 100 / 5

        self.logger.info("extracted rating dict =  {0} for review {1}".format(
            rating_dict,
            self.parse_title()))

        return rating_dict