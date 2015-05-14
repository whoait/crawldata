"""
Parser functions
"""
from BeautifulSoup import BeautifulSoup
import requests
import re
from selenium import webdriver

import os
from ..base.parse_hotel import BaseHotel
from ..string_util import filter_description
from .util import get_site_id, trim_url_query_string, split_line


class BookingHotel(BaseHotel):
    # BaseHotel receives soup for hotel listing
    def __init__(self, driver, base_url, entity_id):
        super(BookingHotel, self).__init__(driver, base_url)
        self.soup = BeautifulSoup(
            requests.get(base_url)._content)
        # dict to map website aspects to our terminology
        # website term : our term
        self.rating_translation_table = {
            "data-total_hotel_value"    : "Value",
            "data-total_hotel_location" : "Location",
            "data-total_hotel_comfort"  : "Sleep Quality",
            "data-total_hotel_services" : "Facility",
            "data-total_hotel_clean"    : "Cleanliness",
            "data-total_hotel_staff"    : "Service"
            }
        self.entity_id = entity_id

    def parse_name(self):
        name_soup = self.soup.find(attrs={"id": "hp_hotel_name"})
        if name_soup:
            return name_soup.text
        return None

    def parse_source_entity_id(self):
        return self.entity_id

    def parse_source(self):
        return "Booking"

    def parse_address(self):
        address_soup = self.soup.find("span", attrs={"id": "hp_address_subtitle"})
        if address_soup:
            return address_soup.text
        return None

    def parse_review_count(self):
        try:
            return int(
                self.soup.
                    find("div", attrs={"id": "usp_review"}).
                    find("p", attrs={"class": "usp_heading"}).
                    text.split(" verified")[0])
        except:
            self.logger.info("cannot parse max count from hotel_url = {0}".
                format(self.base_url))
        return None

    def parse_postcode(self):
        return None

    def parse_lat(self):
        address_soup = self.soup.find("span", attrs={"id": "hp_address_subtitle"})
        if address_soup:
            try:
                return float(
                    address_soup['data-coords'].
                    split(",")[1]
                )
            except:
                self.logger.info(
                    "could not parse latitude for url = {0}".
                    format(self.base_url))
        return None

    def parse_lng(self):
        address_soup = self.soup.find("span", attrs={"id": "hp_address_subtitle"})
        if address_soup:
            try:
                return float(
                    address_soup['data-coords'].
                    split(",")[0]
                )
            except:
                self.logger.info(
                    "could not parse longitude for url = {0}".
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
        return trim_url_query_string(self.base_url)

    def parse_phone(self):
        return None

    def parse_description(self):
        # booking.com carries a description
        description_soup = self.soup.find("div", attrs={"id": "summary"})
        if description_soup:
            return filter_description(str(description_soup))
        return None

    def parse_short_description(self):
        return None

    def parse_avatar(self):
        photo_wrapper = self.soup.find("div", attrs={"id": "photo_wrapper"})
        if photo_wrapper:
            if photo_wrapper.find("img"):
                return photo_wrapper.find("img")['src']
        return None

    def parse_all_photos(self):
        photo_list = []
        photo_list_soup = self.soup.find(id="photos_distinct")
        if photo_list_soup:
            for photo_soup in photo_list_soup.findAll("a"):
                photo_list.append(
                    str(photo_soup).
                    split('data-resized="')[1].
                    split('"')[0]
                )
        return photo_list

    def parse_entity_source_rating(self):
        rating_dict = {}
        # find overall rating
        try:
            overall_soup = self.soup.find(
                               "div",
                               attrs={"id": "review_list_main_score"})
            rating_dict['overall'] = float(overall_soup['data-total']) * 100 / 10
        except:
            self.logger.info("Cannot get overall rating from soup: {0}".format(overall_soup))

        # extract subscores
        rating_soup = self.soup.find("ul", attrs={"id": "review_list_score_breakdown"})
        for key in self.rating_translation_table:
            try:
                rating_dict[self.rating_translation_table[key]] = float(rating_soup[key]) * 100 / 10
            except:
                self.logger.info("No rating for key {0} in soup {1}".format(key, rating_soup))

        self.logger.info("extracted rating dict =  {0} for hotel {1}".format(
            rating_dict,
            self.parse_name()))

        return rating_dict

    def parse_amenity(self):
        amenity_dict = {}
        amenity_soup = self.soup.find(
            id="hp_facilities_box"
        )
        if amenity_soup:
            common_amenity_soup = amenity_soup.find("div", "common_room_facilities")
            if common_amenity_soup:
                common_amenity_list = common_amenity_soup.findAll("div")
                for amenity in common_amenity_list:
                    if len(amenity.findAll("p")) >= 2:
                        key_str = amenity.find("span").text if amenity.find("span") else None
                        soup_list = [n for n in filter(
                                lambda x:
                                    'facility_name' !=
                                (x.get('class') or ""),
                                amenity.findAll("p")
                            )]

                        val_list_2d = [
                            map(split_line, soup_list)
                        ]
                        val_list = []
                        for val_list_1d in val_list_2d:
                            for val_item in val_list_1d:
                                val_list += val_item
                        if key_str:
                            amenity_dict[key_str] = val_list
                    else:
                        pass
        return amenity_dict
