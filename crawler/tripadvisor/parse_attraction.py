"""
Parser functions
"""
from BeautifulSoup import BeautifulSoup
import urllib2
from selenium import webdriver

import os
from ..base.parse_hotel import BaseHotel


class TripadvisorAttraction(BaseHotel):
    # BaseHotel receives soup for hotel listing
    def __init__(self, driver, base_url):
        super(TripadvisorAttraction, self).__init__(driver, base_url)
        self.driver.get(self.base_url)
        self.soup = BeautifulSoup(
            self.driver.page_source)
        # dict to map website aspects to our terminology
        # website term : our term
        self.rating_translation_table = {
            "Value"		: "Value",
            "Location"	: "Location",
            "Sleep Quality"	: "Sleep Quality",
            "Room"		: "Room",
            "Cleanliness"	: "Cleanliness",
            "Service"	: "Service"
            }

    def parse_name(self):
        return (self.soup.find("h1").
            text.strip())

    def parse_source_entity_id(self):
        try:
            return int(self.base_url.split("-d")[1].split("-")[0])
        except:
            entity_id = 0
        self.logger.info("hotel_id cannot be read from " + self.base_url)
        return None

    def parse_source(self):
        return "Tripadvisor"

    def parse_address(self):
        try:
            return self.soup.find(property="v:street-address").text
        except:
            self.logger.info(
                "could not parse address for url = {0}".
                format(self.base_url))
        return None

    def parse_postcode(self):
        try:
            return self.soup.find(property='v:postal-code').text
        except:
            self.logger.info(
                "could not parse postcode for url = {0}".
                format(self.base_url))
        return None

    def parse_lat(self):
        if self.soup.find("div", "staticMap") and self.soup.find("div", "staticMap").find("img"):
            try:
                latlng = (self.soup.find(id='STATIC_MAP').
                    find('img')['src'].
                    split('center=')[1].
                    split('&')[0])
                return float(latlng.split(',')[0])
            except:
                self.logger.info(
                    "could not parse latitude for soup = {0}".
                    format(self.soup.find(id="STATIC_MAP").find("img")))
        else:
            self.logger.info("No map found.")
        return None

    def parse_lng(self):
        if self.soup.find("div", "staticMap") and self.soup.find("div", "staticMap").find("img"):
            try:
                latlng = (self.soup.find(id='STATIC_MAP').
                    find('img')['src'].
                    split('center=')[1].
                    split('&')[0])
                return float(latlng.split(',')[1])
            except:
                self.logger.info(
                    "could not parse latitude for soup = {0}".
                    format(self.soup.find(id="STATIC_MAP").find("img")))
        else:
            self.logger.info("No map found.")
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
        # check if the email exists:
        contact_soup = self.soup.find("div", "odcHotel")
        if contact_soup:
            contact_list = contact_soup.findAll("div", "contact_item")
        else:
            contact_list = []
        for item in contact_list:
            if item.find("div", "grayEmail"):
                # we have an email address - ask for it!
                source_entity_id = self.parse_source_entity_id()
                request_email_url = (
                    "http://www.tripadvisor.com/EmailHotel?detail={0}&isOfferEmail=false&overrideOfferEmail=".
                    format(source_entity_id))
                # we only need an email address
                # urllib2 is faster than selenium webdriver
                email_soup = BeautifulSoup(
                    urllib2.urlopen(request_email_url).read())
                try:
                    return (email_soup.find(
                        "input","emailOwnerReadonly")
                        ["value"])
                except:
                    self.logger.info(
                        "could not extract email with request_url = {0} for url = {1}".
                        format(request_email_url, self.base_url))
        return None

    def parse_website(self):
    # /ShowUrl?&excludeFromVS=false&odc=BusinessListingsUrl&d=4341475&url=1
        contact_soup = self.soup.find("div", "odcHotel")
        if contact_soup:
            contact_list = contact_soup.findAll("div", "contact_item")
        else:
            contact_list = []
        for item in contact_list:
            if item.find("div", "grayWeb"):
                # we have url link - got to it!
                source_entity_id = self.parse_source_entity_id()
                request_url = (
                    "{0}/ShowUrl?&excludeFromVS=false&odc=BusinessListingsUrl&d={1}&url=1".
                    format(self.base_url, source_entity_id))
                try:
                    return urllib2.urlopen(request_url).geturl()
                except:
                    self.logger.info(
                        "could not extract website url for url = {0}".
                        format(self.base_url))
        return None

    def parse_phone(self):
        contact_soup = self.soup.find("div", "odcHotel")
        if contact_soup:
            contact_list = contact_soup.findAll("div", "contact_item")
        else:
            contact_list = []
        for item in contact_list:
            if item.find("div", "grayPhone"):
                try:
                    item.find("script").decompose()
                except:
                    # item has no script
                    pass
                return str(item.text)

    def parse_description(self):
        # no description available
        return None

    def parse_short_description(self):
        return None

    def parse_avatar(self):
        try:
            return self.soup.find("div", "full_meta_photo").find("img")['src']
        except:
            # no full size photo - try to get smaller photo
            try:
                return self.soup.find("img", "photo_image")['src']
            except:
                self.logger.info(
                    "could not extract avatar for url = {0}".
                    format(self.base_url))
        return None

    def parse_entity_source_rating(self):
        rating_dict = {}
        # find overall rating
        rating_soup = self.soup.find(id="REVIEW_FILTER_FORM")
        if rating_soup:
            overall_soup = rating_soup.find("ul", "barChart")
            if overall_soup:
                rating_list = overall_soup.findAll("div", "row")
                if len(rating_list) != 5:
                    raise Exception("unexpected length of rating list: {0} for url = {1}".
                        format(len(rating_list),
                        self.base_url))
                vote_count_list = []
                for item in rating_list:
                    try:
                        vote_count_list.append(
                            int(item.find(
                            "span", "compositeCount").
                            text.replace(",","")))
                    except:
                        self.logger.info(
                            "unexpected syntax of rating {0} for item {1} at url: {2}".
                            format(
                                item.find(
                                    "span", "compositeCount"),
                            item,
                            self.base_url))
                        return None
                rating_cursor = 100
                total_vote_score = 0
                total_vote_count = 0
                for vote_count in vote_count_list:
                    total_vote_score += rating_cursor * vote_count
                    total_vote_count += vote_count
                    rating_cursor -= 20 # 100/len(rating_list)
                rating_dict['overall'] = total_vote_score / total_vote_count

            # find per-aspect rating
            aspect_raw_soup = rating_soup.find(
                id="SUMMARYBOX")
            if aspect_raw_soup:
                aspect_soup = aspect_raw_soup.find("ul")
                if aspect_soup:
                    aspect_list = aspect_soup.findAll("li")
                    for aspect in aspect_list:
                        name = aspect.find("div","name").text
                        try:
                            score_string = aspect.find("img")["alt"]
                            raw_score = float(
                                score_string.
                                split(' of ')[0])
                            scale = float(
                                score_string.
                                split(' of ')[1].
                                split(' stars')[0])
                            rating_dict[name] = 100*raw_score/scale
                        except:
                            self.logger.info(
                                "unexpected syntax of rating aspect {0} at url {2}".
                                format(aspect, self.base_url))
        return rating_dict

    def parse_open_time(self):
        return None

    def parse_prices(self):
        return None
