"""
Parser functions
"""
from BeautifulSoup import BeautifulSoup, NavigableString, Tag
from selenium import webdriver
import datetime
import urllib2

from ..base.parse_review import BaseReview


class TripadvisorReview(BaseReview):

    def __init__(self, driver, base_url, soup):
        super(TripadvisorReview, self).__init__(driver, base_url)

        if soup:
            self.driver = driver
            self.soup = soup
            #self.logger.info("Logging with pre-supplied soup")
            #self.logger.info(self.soup)
            self.review_soup = soup
            try:
                self.logger.info("soup attrs = {0}".format(self.soup.attrs))
                self.review_id = int(
                    self.soup.get('id').
                    split("review_")[1])
            except:
                self.review_id = 0
                self.logger.info(
                    "cannot assign review_id to soup = {0}".
                    format(self.base_url))
            try:
                self.entity_source_id = int(
                    self.base_url.split("-d")[1].
                    split('-')[0])
            except:
                self.entity_source_id = 0
                self.logger.info(
                    "cannot assign entity_source_id to url = {0}".
                    format(self.base_url))
        else:
            self.driver.get(self.base_url)
            self.soup = BeautifulSoup(
                self.driver.page_source)
            try:
                self.review_id = int(
                    self.base_url.split("-r")[1].
                    split('-')[0])
            except:
                self.review_id = 0
                self.logger.info(
                    "cannot assign review_id to url = {0}".
                    format(self.base_url))
            try:
                self.entity_source_id = int(
                    self.base_url.split("-d")[1].
                    split('-')[0])
            except:
                self.entity_source_id = 0
                self.logger.info(
                    "cannot assign entity_source_id to url = {0}".
                    format(self.base_url))
            # review_soup
            self.review_soup = self.soup.find("div", id="review_{0}".format(self.review_id))
            if not self.review_soup:
                self.review_soup = self.soup.find("div", "entry")
            else:
                self.logger.info(
                    "cannot obtain review_soup for url = {0}".
                    format(self.base_url))
        ## try using urllib2 here:
        # NO URLLIB - it defaults to ascii
        #self.soup = BeautifulSoup(
        #	urllib2.urlopen(self.base_url).read())
        # initialized commonly reused fields
        # review_id


        # member_soup
        self.member_soup = self.soup.find("div", "member_info")
        if not self.member_soup:
            self.logger.info(
                "cannot obtain member_soup for url = {0}".
                format(self.base_url))
        self.rating_translation_table = {
            "Value"		: "Value",
            "Location"	: "Location",
            "Sleep Quality"	: "Sleep Quality",
            "Room"		: "Room",
            "Cleanliness"	: "Cleanliness",
            "Service"	: "Service"
            }


    def parse_source(self):
        return "Tripadvisor"

    def parse_title(self):
        if self.review_soup:
            return self.review_soup.find("div", "quote").text

    def parse_site_id(self):
        return self.review_id

    def parse_username(self):
        if self.member_soup:
            return self.member_soup.find("div", "username").text
        return None

    def parse_user_id(self):
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

    def parse_date(self):
        if self.review_soup:
            date_soup = self.review_soup.find("span", "ratingDate")
            if date_soup:
                date_string = date_soup.get('content')
                if date_string:
                    date_array = date_string.split('-')
                    self.logger.info("date array = {0}".format(date_array))
                    try:
                        year_int = int(date_array[0])
                        month_int = int(date_array[1])
                        day_int = int(date_array[2])
                        self.logger.info("year int = {0}, month int = {1}, day int = {2}".format(year_int, month_int, day_int))
                        return datetime.datetime(
                            year_int,
                            month_int,
                            day_int, 0,0,0)
                    except:
                        self.logger.info(
                            "invalid review date {0} from url = {1}".
                            format(date_string, self.base_url))
                else:
                    date_string = date_soup.text.replace("NEW", "")
                    return datetime.datetime.strptime(
                        date_string.split("Reviewed ")[1],
                        "%d %B %Y"
                    )
        return None

    def parse_review_text(self):
        if self.review_soup:
            if self.review_soup.find("span", "moreLink"):
                new_url = self.base_url.replace(
                    "-Reviews-",
                    "-r{0}-".format(self.review_id))
                new_url = new_url.replace(
                    "Attraction_Review",
                    "ShowUserReviews")
                self.logger.info("new url = {0}".format(new_url))
                self.driver.get(new_url)
                new_soup = BeautifulSoup(self.driver.page_source)
                self.review_soup = new_soup.find()
                #review_array = self.review_soup.find(
                #    "p", id="review_{0}".format(self.review_id)).contents
                review_array_soup = self.review_soup.find(
                    "div", "entry"
                )
                if review_array_soup:
                    review_array = review_array_soup.text
                    review_string = ""
                    for line in review_array:
                        if isinstance(line, NavigableString):
                            line_string = unicode(line).strip()
                            if not review_string.endswith(' '):
                                review_string += ' '
                            review_string += line_string
                    return review_string
            else:
                review_string = self.review_soup.find("div", "entry").text
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
        # overall rating
        if self.review_soup:
            overall_soup = self.review_soup.find("div", "rating")
            if overall_soup:
                overall_string = overall_soup.find("img").get('alt')
                if overall_string:
                    raw_score = float(
                        overall_string.
                        split(' of ')[0])
                    scale = float(
                        overall_string.
                        split(' of ')[1].
                        split(' stars')[0])
                    rating_dict['overall'] = 100*raw_score/scale
            aspect_soup = self.review_soup.find("ul", "recommend")
            if aspect_soup:
                aspect_list = aspect_soup.findAll("li", "recommend-answer")
                if aspect_list and len(aspect_list) > 0:
                    for aspect in aspect_list:
                        try:
                            aspect_name = aspect.text
                            # catch illegal aspect names that confuse mongo bson
                            # record new names: don't use strict list yet at mongo stage
                            if "." in aspect_name:
                                aspect_name = aspect_name.replace('.', '')
                            if "(" in aspect_name:
                                aspect_name = aspect_name.split("(")[0].strip()
                            aspect_rating_string = (aspect.
                                find("img").get('alt'))
                            aspect_score = float(
                                aspect_rating_string.
                                split(' of ')[0])
                            aspect_scale = float(
                                aspect_rating_string.
                                split(' of ')[1].
                                split(' stars')[0])
                            rating_dict[aspect_name] = (
                                100*aspect_score/aspect_scale)
                        except:
                            self.logger.info(
                                "unexpected syntax of rating {0} for url {1}".
                                format(aspect, self.base_url))
            # tripadvisor should at least have an overall rating
            if len(rating_dict) == 0:
                self.logger.info(
                    "zero length dict - from soup {0}:{1} at url {1}".
                    format(overall_soup, self.soup, self.base_url))
                # raise Exception("zero ratings")
        return rating_dict
