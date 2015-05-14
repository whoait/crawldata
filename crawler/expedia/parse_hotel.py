"""
Parser functions
"""
from BeautifulSoup import BeautifulSoup
import requests
from selenium import webdriver

import os
from ..base.parse_hotel import BaseHotel
from ..string_util import filter_description
from .util import get_site_id, trim_url_query_string


class ExpediaHotel(BaseHotel):
    # BaseHotel receives soup for hotel listing
    def __init__(self, driver, base_url):
        super(ExpediaHotel, self).__init__(driver, base_url)
        self.soup = BeautifulSoup(
            requests.get(base_url)._content)
        # dict to map website aspects to our terminology
        # website term : our term
        self.rating_translation_table = {
            "hotelCondition"    : "Facility",
            "roomComfort"       : "Room",
            "cleanliness"       : "Cleanliness",
            "serviceAndStaff"   : "Service"
            }

    def parse_name(self):
        return (self.soup.find("h1").text.strip())

    def parse_source_entity_id(self):
        site_id_value = get_site_id(self.base_url)
        if site_id_value is not None:
            return site_id_value
        else:
            self.logger.info("Site ID is None")
            return None

    def parse_source(self):
        return "Expedia"

    def parse_address(self):
        try:
            map_link = self.soup.find("a", "map-link")
            if map_link:
                address_link = map_link.find("span", "street-address")
                if address_link and address_link.text:
                    return address_link.text
        except:
            self.logger.info(
                "could not parse address for url = {0}".
                format(self.base_url))
        return None

    def parse_postcode(self):
        try:
            map_link = self.soup.find("a", "map-link")
            if map_link:
                postcode_link = map_link.find("span", "postal-code")
                if postcode_link and postcode_link.text:
                    return postcode_link.text
        except:
            self.logger.info(
                "could not parse postcode for url = {0}".
                format(self.base_url))
        return None

    def parse_lat(self):
        try:
            return float(self.soup.
                find(id="location-teaser-map")['style'].
                split("center=")[1].
                split("&")[0].
                split(",")[0])
        except:
            self.logger.info(
                "could not parse latitude for url = {0}".
                format(self.base_url))
        return None

    def parse_lng(self):
        try:
            return float(self.soup.
                find(id="location-teaser-map")['style'].
                split("center=")[1].
                split("&")[0].
                split(",")[1])
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
        # hotels.com carries a description

        description_soup = self.soup.find("div", "hotel-description")
        if description_soup:
            raw_description_list = list(self.soup.findAll("p"))
            return " ".join(
                            map(
                                lambda x: x.text, raw_description_list))

    def parse_short_description(self):
        return None

    def parse_avatar(self):
        try:
            raw_url = self.soup.find("ul", "image-slider-thumbs").find("li").find("a")['href']
            if raw_url:
                fullsize_url = raw_url.replace("b.jpg", "z.jpg")
                return fullsize_url
        except:
            self.logger.info("cannot find avatar for hotel - {0}".format(self.base_url))
            # no full size photo - try to get smaller photo
            # try:
            #     return self.soup.find("img", "")['src']
            # except:
            #     self.logger.info(
            #         "could not extract avatar for url = {0}".
            #         format(self.base_url))
        return None

    def parse_entity_source_rating(self):
        rating_dict = {}
        # find overall rating

        # extract json ratings independently
        url = "http://reviewsvc.expedia.com/reviews/v1/retrieve/getReviewsForHotelId/{0}/?_type=json".format(
            self.parse_source_entity_id()
        )

        rating_dict = requests.get(url).json()
        try:
            summary_dict = rating_dict['reviewDetails']['reviewSummaryCollection']['reviewSummary'][0]["originSummary"][0]
        except:
            self.logger.info("this hovel has no rating - {0}".format(self.base_url))
            return rating_dict

        rating_dict['overall'] = summary_dict['avgOverallRating'] * 100 / 5
        for item in self.rating_translation_table:
            rating_dict[self.rating_translation_table[item]] = summary_dict[item] * 100 / 5

        self.logger.info("extracted rating dict =  {0} for hotel {1}".format(
            rating_dict,
            self.parse_name()))

        return rating_dict
