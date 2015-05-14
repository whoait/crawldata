"""
Parser functions
"""
from BeautifulSoup import BeautifulSoup
import urllib2
from selenium import webdriver

import os
from ..base.parse_hotel import BaseHotel


class AgodaHotel(BaseHotel):
    # BaseHotel receives soup for hotel listing
    def __init__(self, driver, base_url):
        super(AgodaHotel, self).__init__(driver, base_url)
        self.driver.get(self.base_url)
        self.soup = BeautifulSoup(
            self.driver.page_source)
        # dict to map website aspects to our terminology
        # website term : our term
        self.rating_translation_table = {
            "Value"		: "Value for Money",
            "Location"	: "Location",
            "Room"		: "Room Comfort/Standard",
            "Cleanliness"	: "Hotel Condition/Cleanliness",
            "Service"	: "Staff Performance",
            "Food"      : "Food/Dining"
            }
        # popup map contains various attribute information that can be
        # initialized in the constructor
        try:
            info_string = self.soup.find(title="Show hotel on map")['href']
            if "hotel_id" in info_string:
                self.entity_id = int(
                    info_string.
                    split("hotel_id=")[1].
                    split("&")[0])
            else:
                raise Exception("No Entity id")
            if "latitude" in info_string:
                self.latitude = float(
                    info_string.
                    split("latitude=")[1].
                    split("&")[0])
            if "longitude" in info_string:
                self.longitude = float(
                    info_string.
                    split("longitude=")[1].
                    split("&")[0])
            if ((self.latitude is None and self.longitude is not None) or
                    (self.latitude is not None and self.longitude is None)):
                raise Exception("Cannot have latitude without longitude!")
        except:
            raise Exception("Information String missing")

    def parse_name(self):
        h1_soup = self.soup.find("h1")
        if h1_soup:
            if h1_soup.find("span"):
                return h1_soup.find("text")
        return None

    def parse_source_entity_id(self):
        return self.entity_id

    def parse_source(self):
        return "Agoda"

    def parse_address(self):
        try:
            return self.soup.find("p", "fontsmalli sblueboldunder").text.split("\n")[0]
        except:
            self.logger.info(
                "could not parse address for url = {0}".
                format(self.base_url))
        return None

    def parse_postcode(self):
        return None

    def parse_lat(self):
        return self.latitude

    def parse_lng(self):
        return self.longitude

    def parse_city(self):
        # should be passed directly to hotel as arg
        raise NotImplementedError()

    def parse_country(self):
        # should be passed directly to hotel as arg
        raise NotImplementedError()

    def parse_category(self):
        # should be passed directly to hotel as arg
        #raise NotImplementedError()
        return "hotel"

    def parse_email(self):
        return None

    def parse_website(self):
        return self.driver.current_url.split("?")[0]

    def parse_phone(self):
        return None

    def parse_description(self):
        # no description available
        desc_soup = self.soup.find(id="hotelDescription")
        if desc_soup:
            return desc_soup.text
        return None

    def parse_short_description(self):
        short_desc_soup = self.soup.find(id="snippetHotelDescription")
        if short_desc_soup:
            return short_desc_soup.text
        return None

    def parse_avatar(self):
        try:
            return self.soup.find(id="hotelPic")['src']
        except:
            self.logger.info(
                "could not extract avatar for url = {0}".
                format(self.base_url))
        return None

    def parse_entity_source_rating(self):
        rating_dict = {}
        # find overall rating
        rating_soup = self.soup.find(
            id="ctl00_ctl00_MainContent_ContentMain_HotelReview1_lblTotalScore")
        if rating_soup:
            rating_score = float(rating_soup.text) * 100 / 10
            rating_dict['overall'] = rating_score

        # find per-aspect rating
        aspect_soup = self.soup.find(id="ctl00_ctl00_MainContent_ContentMain_HotelReview1_Table1")
        if aspect_soup:
            rating_list_soup = aspect_soup.findAll("tr")
            if rating_list_soup:
                for item in rating_list_soup:
                    aspect_score_list = item.find("span")
                    if aspect_score_list and len(aspect_score_list) >= 2:
                        rating_score = float(aspect_score_list) * 100 / 10
                        rating_dict[
                            self.rating_translation_table[
                                aspect_score_list[0]]] = rating_score

        return rating_dict
