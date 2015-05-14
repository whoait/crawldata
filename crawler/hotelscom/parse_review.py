"""
Parser functions
"""
from BeautifulSoup import BeautifulSoup, NavigableString, Tag
from selenium import webdriver
import datetime
import urllib2
import traceback

from ..base.parse_review import BaseReview
from crawler.string_util import strip_punctuation_whitespace


class HotelscomReview(BaseReview):

    def __init__(self, driver, base_url, soup):
        super(HotelscomReview, self).__init__(driver, base_url)
        # reviews done in bulk - no need to parse each one
        # self.driver.get(self.base_url)

        self.soup = soup

        ## try using urllib2 here:
        # NO URLLIB - it defaults to ascii
        #self.soup = BeautifulSoup(
        #	urllib2.urlopen(self.base_url).read())
        # initialized commonly reused fields


        try:
            self.entity_source_id = int(
                self.base_url.split("/hotel/")[1].
                split('/reviews/')[0])
        except:
            self.entity_source_id = 0
            self.logger.info(
                "cannot assign entity_source_id to url = {0}".
                format(self.base_url))
        # review_soup

        self.review_soup = self.soup
        if not self.review_soup:
            self.logger.info(
                "cannot obtain review_soup for url = {0}".
                format(self.base_url))

        # member_soup
        self.member_soup = self.soup.find("div", "reviewer")
        if not self.member_soup:
            self.logger.info(
                "cannot obtain member_soup for url = {0}".
                format(self.base_url))

        self.rating_translation_table = {
            "Value"		: "Value",
            "Neighbourhood"	: "Location",
            "Comfort"	: "Sleep Quality",
            "Condition"		: "Room",
            "Cleanliness"	: "Cleanliness",
            "Service"	: "Service"
        }
        self.date_map = {
            'Jan': 1,
            'Feb': 2,
            'Mar': 3,
            'Apr': 4,
            'May': 5,
            'Jun': 6,
            'Jul': 7,
            'Aug': 8,
            'Sep': 9,
            'Oct': 10,
            'Nov': 11,
            'Dec': 12
        }

                # review_id

        # as no review_id is visible - we need our own hasing scheme
        # to generate a reproducible site review_id to detect previously
        # crawled entries.

        self.review_id = self.build_review_id()

            # print traceback.format_exc()
            # self.logger.info(
            #     "cannot build review_id for soup = {0}".format(
            #     self.soup))
            # self.review_id = "0"


    def parse_source(self):
        return "Hotelscom"

    def parse_title(self):
        if self.review_soup:
            quotation_soup = self.review_soup.find("q", "summary")
            if quotation_soup:
                return quotation_soup.text.strip().replace('"', '')
        return None

    def parse_site_id(self):
        return self.review_id

    def parse_username(self):
        if self.member_soup:
            # need place_from to split the text string from members
            place_from_string = self.parse_place_from()
            if place_from_string:
                return self.member_soup.find("span").text.split(place_from_string)[0]
        return None        # we can retrieve a user id from the site - so we're going to assume each review is different


    def parse_user_id(self):
        # we can retrieve a user id from the site - so we're going to assume each review is different
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
        if self.member_soup:
            member_location = self.member_soup.find("div", "location")
            if member_location:
                return member_location.text
        return None

    def parse_helpful(self):
        if self.review_soup:
            helpful_soup = self.review_soup.find("div", "helpful")
            if helpful_soup:
                helpful_count = helpful_soup.find("span", "numHlp")
                if helpful_count:
                    return int(helpful_count.text)
                # we return 0 here to differentiate reviews
                # with 0 helpful votes from reviews without
                # the helpful attribute
                else:
                    return 0
        return None

    def parse_raw_date(self):
        if self.review_soup:
            date_soup = self.review_soup.find("span", "dtreviewed")
            if date_soup:
                date_string = date_soup.text
                return date_string
        return None

    def parse_date(self):
        date_string = self.parse_raw_date()
        if date_string:
            date_array = date_string.split('in ')[1].split(' ')

            year_int = int(date_array[1])
            month_int = self.date_map[date_array[0]]
            day_int = 1
            # self.logger.info("date array = {0}".format(date_array))

            return datetime.datetime(
                year_int,
                month_int,
                day_int, 0, 0, 0)
        return None

    # needed for Hotels.com - they feature Expedia reviews and we don't want
    # to store those twice!
    def parse_origin(self):
        genuine_soup = self.review_soup.find("div", "genuine-msg")
        if genuine_soup:
            genuine_string = genuine_soup.text
            if "Hotels.com" in genuine_string:
                return True
        return False

    # because hotels.com doesn't have a review_id - we need to build one
    def build_review_id(self):
        # composite IDs from
        # 1) reviewer
        # 2) locale
        # 3) date
        # 4) text
        reviewer_locale = self.member_soup.text
        date = self.parse_raw_date()
        text = self.parse_review_text()[:100]
        if reviewer_locale and date and text:
            return ((reviewer_locale +
                     date +
                    text).replace(' ', '')[:32])
        return None

    def parse_review_text(self):
        if self.review_soup:
            review_string = self.review_soup.find(
                "blockquote", "description"
            ).text
            if review_string:
                review_string = (review_string.
                    replace("&nbsp;[&hellip;]&nbsp;", " ").
                    replace("\n\n", "\n").
                    replace("\n", " "))
                return review_string
        return None

    def parse_review_positive(self):
        return None

    def parse_review_negative(self):
        return None

    def parse_entity_source_id(self):
        return self.entity_source_id

    def parse_review_rating(self):
        rating_dict = {}
        rating_soup = self.review_soup.find()
        # overall rating
        if rating_soup:
            rating_list_soup = rating_soup.find("ul", "ratings-list")
            if rating_list_soup:
                rating_aspect_list = list(
                    rating_list_soup.findAll("li", "rating")
                )
                for aspect in rating_aspect_list:
                    try:
                        aspect_name = aspect.find("h5", "label").text
                        translated_aspect_name = (
                            self.rating_translation_table.get(aspect_name))
                        aspect_rating = float(
                            aspect.find("span", "value").text)
                        # normalize internal ratings to /100 from /5
                        rating_dict[translated_aspect_name] = 100*aspect_rating/5.0
                    except:
                        self.logger.info("Parsing error for {0}".format(aspect))
                        continue
        return rating_dict