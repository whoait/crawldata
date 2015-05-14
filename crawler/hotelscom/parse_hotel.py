"""
Parser functions
"""
from BeautifulSoup import BeautifulSoup
import requests
from selenium import webdriver

import os
from ..base.parse_hotel import BaseHotel
from crawler.string_util import filter_description


class HotelscomHotel(BaseHotel):
    # BaseHotel receives soup for hotel listing
    def __init__(self, driver, base_url):
        super(HotelscomHotel, self).__init__(driver, base_url)
        self.soup = BeautifulSoup(
            requests.get(base_url)._content)
        # dict to map website aspects to our terminology
        # website term : our term
        self.rating_translation_table = {
            "Value"		: "Value",
            "Neighbourhood"	: "Location",
            "Comfort"	: "Sleep Quality",
            "Condition"		: "Room",
            "Cleanliness"	: "Cleanliness",
            "Service"	: "Service"
            }

    def parse_name(self):
        return (self.soup.find("h1", "fn org").
            text.strip())

    def parse_source_entity_id(self):
        try:
            return int(self.base_url.split("&hotelId=")[1].split("&")[0])
        except:
            entity_id = 0
        self.logger.info("hotel_id cannot be read from " + self.base_url)
        return None

    def parse_source(self):
        return "Hotelscom"

    def parse_address(self):
        try:
            return self.soup.find("span", "street-address").text.strip()
        except:
            self.logger.info(
                "could not parse address for url = {0}".
                format(self.base_url))
        return None

    def parse_postcode(self):
        try:
            return (self.soup.find("span", "postal-code").
                    text.strip().split(',')[0])
        except:
            self.logger.info(
                "could not parse postcode for url = {0}".
                format(self.base_url))
        return None

    def parse_lat(self):
        try:
            return float(self.soup.find("span", "latitude").
                         text.strip())
        except:
            self.logger.info(
                "could not parse latitude for url = {0}".
                format(self.base_url))
        return None

    def parse_lng(self):
        try:
            return float(self.soup.find("span", "longitude").
                         text.strip())
        except:
            self.logger.info(
                "could not parse latitude for url = {0}".
                format(self.base_url))
        return None

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
    # /EmailHotel?detail=4341475&isOfferEmail=false&overrideOfferEmail=
    # No email for Hotels.com
        return None

    def parse_website(self):
    # /ShowUrl?&excludeFromVS=false&odc=BusinessListingsUrl&d=4341475&url=1
        return None

    def parse_phone(self):
        return None

    def parse_description(self):
        # hotels.com carries a description
        raw_description = str(
            self.soup.find("div", "info-box"))

        return filter_description(raw_description)

    def parse_short_description(self):
        return None

    def parse_avatar(self):
        try:
            return self.soup.find("div", "slide active").find("img")['src']
        except:
            # no full size photo - try to get smaller photo
            try:
                return self.soup.find("img", "")['src']
            except:
                self.logger.info(
                    "could not extract avatar for url = {0}".
                    format(self.base_url))
        return None

    def parse_entity_source_rating(self):
        rating_dict = {}
        # find overall rating

        rating_soup = self.soup.find("span", "rating hidden")

        if rating_soup:
            overall_soup = rating_soup.find("span", "average")
            if overall_soup:
                text_rating = overall_soup.text
                float_rating = float(text_rating)
                rating_dict['overall'] = float_rating * 100 / 5

        """
        Extract the other aspects
        Init second call
        """
        rating_soup = BeautifulSoup(
            requests.get(
                "http://sg.hotels.com/hotel/{0}/reviews/?reviewOrder=date_newest_first&tripTypeFilter=all#".
                format(self.parse_source_entity_id())
            )._content
        )
        if rating_soup:
            rating_list_soup = rating_soup.find("ul", "ratings")
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
