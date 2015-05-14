"""
Parser functions
"""
from BeautifulSoup import BeautifulSoup, NavigableString, Tag
from selenium import webdriver
import time
import datetime
import urllib2

from ..base.parse_review import BaseReview
from ..string_util import filter_description


class AgodaReview(BaseReview):

    def __init__(self, driver, base_url, soup, entity_source_id, id_index):
        super(AgodaReview, self).__init__(driver, base_url)
        # self.driver.get(self.base_url)
        self.soup = soup
        ## try using urllib2 here:
        # NO URLLIB - it defaults to ascii
        #self.soup = BeautifulSoup(
        #	urllib2.urlopen(self.base_url).read())

        # initialized commonly reused fields
        # review_id - resonable to assume presence of report link
        try:
            self.review_id = int(
                self.soup.find(title="Report this review")['onclick'].
                split("this.id, '")[1].
                split("&")[0]
                )
        except:
            self.review_id = 0
            self.logger.info(
                "cannot assign review_id to url = {0}".
                format(self.base_url))
        self.entity_source_id = entity_source_id
        self.id_index = id_index
        self.rating_translation_table = {
            "Value"		: "Value for Money",
            "Location"	: "Location",
            "Room"		: "Room Comfort/Standard",
            "Cleanliness"	: "Hotel Condition/Cleanliness",
            "Service"	: "Staff Performance",
            "Food"      : "Food/Dining"
            }


    def parse_source(self):
        return "Agoda"

    def parse_title(self):
        title_soup = self.soup.find("div", "blue fontmediumb")
        if title_soup:
            return filter_description(title_soup.text)
        return None

    def parse_site_id(self):
        return self.review_id

    def parse_username(self):
        return self.soup.find(
            id="ctl00_ctl00_MainContent_ContentMain_HotelReview1_rptHotelReviews_ctl{0:02}_lblMemberName".format(
                self.id_index)
        ).text

    def parse_user_id(self):
        return None

    def parse_place_from(self):
        return self.soup.find(
            id="ctl00_ctl00_MainContent_ContentMain_HotelReview1_rptHotelReviews_ctl{0:02}_lblMemberNationality".format(
                self.id_index)
        ).text.replace(',', '').strip()

    def parse_helpful(self):
        return None

    def parse_date(self):
        if self.soup:
            date_soup = self.soup.find(
                id="ctl00_ctl00_MainContent_ContentMain_HotelReview1_rptHotelReviews_ctl{0:02}_lblReviewDate".format(
                    self.id_index)
            )
            if date_soup:
                date_string = date_soup.text
                if date_string:
                    return datetime.datetime.strptime(date_string, "%B %d, %Y")
        return None

    def parse_review_text(self):
        if self.soup:
            review_soup = self.soup.find(
                id="ctl00_ctl00_MainContent_ContentMain_HotelReview1_rptHotelReviews_ctl{0:02}_lblCommentText".format(
                    self.id_index)
            )
            if review_soup:
                return review_soup.text.strip()
        return None

    def parse_review_positive(self):
        if self.soup:
            plus_soup = self.soup.find("p", "green")
            if plus_soup:
                return plus_soup.text.strip()
        return None

    def parse_review_negative(self):
        return None

    def parse_entity_source_id(self):
        # assume self.entity_source_id - if not exception would have been raised
        return self.entity_source_id

    def parse_review_rating(self):
        rating_dict = {}
        # overall rating
        if self.soup:
            rating_soup = self.soup.find(
                id="ctl00_ctl00_MainContent_ContentMain_HotelReview1_rptHotelReviews_ctl{0:02}_lblGuestRating".format(
                    self.id_index)
            )
            if rating_soup:
                rating_dict["overall"] = float(rating_soup.text) * 100 / 10
        return rating_dict
