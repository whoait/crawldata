"""
Base Crawler Rules
Rules help the crawler locate links in webpages
"""
import sys
import os
from BeautifulSoup import BeautifulSoup
import urllib2
import requests

from ..base.crawler import BaseCrawler
from ..string_util import setuplogger

class TripadvisorCrawler(BaseCrawler):

    def __init__(self, site_base_url):
        self.site_base_url = site_base_url
        self.logger = setuplogger(loggername='tripadvisor_crawler')

    def crawl_attractions(self, base_url, metadata_dict={}):
        attraction_url_list = []
        url_separator = "Activities-" + metadata_dict['full_name']
        city_url = "{0}/Attractions-g{1}-{2}.html".format(
            self.site_base_url,
            metadata_dict['cityID'],
            url_separator)
        counter = 0

        requests_counter = 0
        while requests_counter < 3:
            try:
                r = requests.get(city_url)
                break
            except requests.exceptions.ConnectionError:
                requests_counter += 1
                continue

        while r.url == city_url:
            list_soup = BeautifulSoup(
                r.text)
            if list_soup.find(id="FILTERED_LIST"):
                for entry in list_soup.findAll("div", "element_wrap"):
                    child_attraction_list = entry.findAll("div", "child_attraction")
                    if len(child_attraction_list) > 0:
                        for child_entry in child_attraction_list:
                            url = child_entry.find("a").get("href")
                            if url:
                                attraction_url_list.append(self.site_base_url + url)
                    else:
                        url = entry.find("a").get('href')
                        if url:
                            attraction_url_list.append(self.site_base_url + url)
            counter += 30
            url_separator = "Activities-oa{0}-".format(counter) + metadata_dict['full_name']
            city_url = "{0}/Attractions-g{1}-{2}.html".format(
                self.site_base_url,
                metadata_dict['cityID'],
                url_separator)
            requests_counter = 0
            while requests_counter < 3:
                try:
                    r = requests.get(city_url)
                    break
                except requests.exceptions.ConnectionError:
                    requests_counter += 1
                    continue
            if requests_counter == 3:
                # go find reviews for another attraction.
                break
        return attraction_url_list

    def crawl_attraction_reviews(self, base_url, metadata_dict={}):
        pass

    # returns list of URLs of all hotels to parse
    # expected contents of meta_dict:
    #  - full_name (of city)
    #  - city ID (tripadvisor)
    #  - country (name)
    def crawl_hotels(self, base_url, metadata_dict={}):
        hotel_url_list = []
        # we'll construct the URL for tripadvisor ourselves
        url_separator = metadata_dict['full_name']+"-Hotels.html"

        city_url = "{0}/Hotels-g{1}-{2}html".format(
            self.site_base_url,
            metadata_dict['cityID'],
            url_separator)

        list_soup = BeautifulSoup(
            urllib2.urlopen(city_url).read())

        # count how many items to put into list
        added_count = 0
        total_count = int(
            list_soup.find(id='MAINWRAP').
                find(id="INLINE_COUNT").
                text.strip().split('of')[0].
                replace(',','').
                replace(' ',''))
        self.logger.info("total_count = {0}".format(total_count))

        while added_count < total_count:
            # collect all divs with hotel links on page
            page_soup = list_soup.find(id="MAINWRAP").find(id="ACCOM_OVERVIEW")
            # self.logger.info("{0}".format(page_soup))
            entry_list = list(
                list_soup.
                find(id="MAINWRAP").
                find(id="ACCOM_OVERVIEW").
                findAll("div", "listing wrap"))
            # iterate through list of all links
            # extract the hotel entry URL into hotel_url_list
            for entry in entry_list:
                hotel_url = (self.site_base_url +
                    entry.
                    find('a','property_title').
                    get('href'))
                hotel_url_list.append(hotel_url)
                added_count += 1
            # load next page if more listings
            if added_count < total_count:
                city_url = "{0}/Hotels-g{1}-oa{2}-{3}".format(
                    self.site_base_url,
                    metadata_dict['cityID'],
                    added_count,
                    url_separator)
                list_soup = BeautifulSoup(
                    urllib2.urlopen(city_url).read())
        return hotel_url_list

    # returns list of review URLs to parse
    # expected contents of metadata_dict
    # - nothing we'll split the base URL
    def crawl_reviews(self, base_url, metadata_dict):
        review_url_list = []
        # we're using the base_url
        list_soup = BeautifulSoup(
            urllib2.urlopen(base_url).read())

        added_count = 0
        total_count = int(
            list_soup.find(id="MAINWRAP").
                find(id="MAIN").
                find(id="HDPR_V1").
                find(id="REVIEWS").
                find("h3").text.split(' ')[0].
                replace(',','').replace(' ',''))

        while added_count < total_count:
            entry_list = list(list_soup.find(id="MAINWRAP").
                find(id="MAIN").
                find(id="HDPR_V1").
                find(id="REVIEWS").
                findAll("div","reviewSelector"))
            for entry in entry_list:
                try:
                    sub_entry = entry.find("div","quote")
                    if not sub_entry:
                        self.logger.info(
                            "invalid entry = {0} at count = {1}/{2} for url {3}. returning".
                            format(entry, added_count, total_count, base_url))
                        # exit early
                        return review_url_list
                    review_url = (self.site_base_url +
                        sub_entry.find('a')['href'])
                    review_url_list.append(review_url)
                    added_count += 1
                except:
                    self.logger.info(
                        "invalid entry = {0} at count = {1} for url {2}".
                        format(entry, added_count, base_url))
            if added_count < total_count:
                new_url_parts = base_url.split('-Reviews-')
                new_url = (new_url_parts[0] +
                    '-Reviews-or{0}-'.format(added_count) +
                    new_url_parts[1])
                list_soup = BeautifulSoup(
                    urllib2.urlopen(new_url).read())

        return review_url_list
