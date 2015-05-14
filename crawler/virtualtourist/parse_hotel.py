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


class VirtualtouristHotel(BaseHotel):
    # BaseHotel receives soup for hotel listing
    def __init__(self, driver, base_url, data_dict):
        super(VirtualtouristHotel, self).__init__(driver, base_url)
        self.soup = BeautifulSoup(
            requests.get(base_url)._content)
        # dict to map website aspects to our terminology
        # website term : our term
        self.rating_translation_table = {
            }
        self.entity_id = data_dict['hotel_id']
        self.overall_rating = data_dict['rating']
        self.stars = data_dict['stars']
        self.lat = data_dict['lat']
        self.lng = data_dict['lng']
        self.review_count = data_dict['review_count']

    def parse_name(self):
        name_soup = self.soup.find("h1")
        if name_soup:
            return name_soup.text
        return None

    def parse_source_entity_id(self):
        return self.entity_id

    def parse_source(self):
        return "Virtualtourist"

    def parse_address(self):
        address_soup = self.soup.find("div", "hotel-address")
        if address_soup:
            return address_soup.text
        return None

    def parse_review_count(self):
        return self.review_count

    def parse_postcode(self):
        return None

    def parse_lat(self):
        return self.lat

    def parse_lng(self):
        return self.lng

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
        return None

    def parse_short_description(self):
        return None

    def parse_avatar(self):
        # virtualtourist has exceptionally bad photos
        return None

    def parse_all_photos(self):
        photo_list = []
        return photo_list

    def parse_stars(self):
        return self.stars

    def parse_entity_source_rating(self):
        rating_dict = {}
        # find overall rating
        rating_dict['overall'] = self.overall_rating * 100 / 5
        return rating_dict

    def parse_amenity(self):
        amenity_dict = {}
        amenity_soup = self.soup.find(
            id="amenities"
        )
        if amenity_soup:
            amenity_list = []
            amenity_list_soup = amenity_soup.findAll("li")
            if amenity_list_soup:
                for item in amenity_list_soup:
                    amenity_list.append(item.text)
            amenity_dict['common'] = amenity_list
        return amenity_dict
