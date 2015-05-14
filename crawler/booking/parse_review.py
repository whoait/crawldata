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


class BookingReview(BaseReview):

    def __init__(self, driver, base_url, soup, entity_source_id):
        super(BookingReview, self).__init__(driver, base_url)
        # reviews extracted via json

        self.soup = soup

        ## try using urllib2 here:
        # NO URLLIB - it defaults to ascii
        #self.soup = BeautifulSoup(
        #	urllib2.urlopen(self.base_url).read())
        # initialized commonly reused fields

        self.entity_source_id = entity_source_id
        self.site_id = self.parse_site_id()
        self.categories = [
                            'Family',
                            'Couple',
                            'Group of friends',
                            'Solo traveler',
                            'Leisure trip',
                            'Business trip',
                            'Traveler with pets'
                            ]

    def parse_generic_id(self, attr_name):
        try:
            return int(
                self.soup.find(
                    "input",
                    attrs={"name": attr_name})['value']
            )
        except:
            self.logger.info(
                "cannot assign site_id to url = {0}".
                format(self.soup))
            raise Exception("Cannot parse ID! Stopping")
        return None

    def parse_source(self):
        return "Booking"

    def parse_title(self):

        return self.soup.find("div", "review_item_header_content").text

    def parse_site_id(self):
        return self.build_review_id()

    def parse_username(self):
        reviewer_soup = self.soup.find("div", attrs={"class": "review_item_reviewer"})
        if reviewer_soup and reviewer_soup.find("h4"):
            return reviewer_soup.find("h4").text.strip()
        return None

    def parse_user_id(self):
        # we cannot retrive a userID from Booking.com
        return None

    def parse_place_from(self):
        reviewer_soup = self.soup.find("div", attrs={"class": "review_item_reviewer"})
        if reviewer_soup and reviewer_soup.find("span",
                attrs={"class": "reviewer_country"}):
            return reviewer_soup.find(
                "span",
                attrs={"class": "reviewer_country"}).text
        return None

    def parse_helpful(self):
        return None

    def parse_date(self):
        date_soup = self.soup.find("div", attrs={"class": "review_item_header_date"})
        if date_soup:
            date_string = date_soup.text
            if date_string:
                return datetime.datetime.strptime(
                    date_string,
                    "%B %d, %Y")
        return None

    def parse_review_text(self):
        # Booking.com only has pos/neg reviews
        return None

    def parse_review_positive(self):
        pos_soup = self.soup.find("p", attrs={"class": "review_pos"})
        if pos_soup:
            return pos_soup.text.strip()
        return None

    def parse_review_negative(self):
        neg_soup = self.soup.find("p", attrs={"class": "review_neg"})
        if neg_soup:
            return neg_soup.text.strip()
        return None

    def parse_entity_source_id(self):
        return self.entity_source_id

    # because hotels.com doesn't have a review_id - we need to build one
    def build_review_id(self):
        # composite IDs from
        # 1) reviewer
        # 2) locale (cancel or there won't be space)
        # 3) date
        # 4) text
        reviewer_locale = self.parse_username()
        date = self.parse_date().strftime("%y%m%d")
        text = (
                (self.parse_review_positive() or "") +
                (self.parse_review_negative() or "")
               )[:100]
        if reviewer_locale and date and text:
            return ((reviewer_locale +
                     date +
                    text).replace(' ', '')[:32])
        return None

    def parse_review_categories(self):
        category_list = []
        category_soup_list = self.soup.find("ul")
        if category_soup_list:
            for item in category_soup_list.findAll("li"):
                category_string = item.text.encode("ascii", "ignore")
                if category_string in self.categories:
                    category_list.append(category_string)
        return category_list

    def parse_review_rating(self):
        rating_dict = {}
        rating_soup = self.soup.find("div", "review_item_review_score")
        if rating_soup:
            try:
                rating_dict['overall'] = float(rating_soup.text) * 100 / 10
            except:
                self.logger.info("cannot parse float for soup = {0}".format(rating_soup))

        #self.logger.info("extracted rating dict =  {0} for review {1}".format(
        #    rating_dict,
        #    self.parse_title()))

        return rating_dict