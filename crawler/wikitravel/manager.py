__author__ = 'ongzhongliang'

"""
TripadvisorManager to manage crawling flow
"""
from selenium import webdriver
from BeautifulSoup import BeautifulSoup
import requests
import pymongo
import time
import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from .crawler import WikitravelCrawler
from ..data.attraction import Attraction
from ..base.manager import BaseManager
from .parse_attraction import WikitravelAttraction
from ..string_util import setuplogger


class WikitravelManager(BaseManager):
    def __init__(self):
        self.logger = setuplogger(loggername="Wikitravel Manager")
        self.driver = webdriver.Firefox()
        self.conn = pymongo.MongoClient()
        self.mongodb = self.conn['hotel_crawler']
        self.crawler = WikitravelCrawler("http://wikitravel.com/en", self.mongodb)

    def __del__(self):
        # self.driver.quit()
        self.conn.disconnect()

    def reload_driver(self):
        self.driver.quit()

    def crawl_attraction(self, filepath=None, skip_flag=False, hotel_only=False, update_existing=False):
        # each entry is place list will have a {url, cityID, city, full_name, country}
        if filepath:
            with open(filepath, "r") as f:
                for line in f:
                    place_dict = json.loads(line)
                    self.logger.info(
                        "loaded place_dict = {0}".
                            format(str(place_dict)))
                    attraction_url_list = self.crawler.crawl_attractions(
                        place_dict['url'],
                        place_dict)

                    for attraction_url in attraction_url_list:
                        self.driver.get(attraction_url)
                        all_soup = BeautifulSoup(self.driver.page_source)
                        for entry_soup in all_soup.findAll("span", "vcard"):
                            attraction_parser = WikitravelAttraction(
                                self.driver,
                                attraction_url,
                                entry_soup)
                            if not self.mongodb.attraction.find_one({
                                    "source_entity_id": attraction_parser.get_site_id(),
                                    "source": "Wikitravel"}):
                                self.logger.info("parsing attraction {0}".format(attraction_parser.parse_source_entity_id()))
                                attraction = Attraction()
                                attraction.set_city(
                                    place_dict['city'],
                                    place_dict['country'])

                                attraction.parse(attraction_parser)
                                attraction.write(self.mongodb, update=True)
                            else:
                                self.logger.info(
                                    "seen attraction {0}".format(attraction_parser.parse_source_entity_id()))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="crawls hotel information from Wikitravel.org")
    parser.add_argument(
        "--file",
        help="file path of text file containing urls to parse")
    parser.add_argument(
        "--skip",
        action="store_true",
        help="if option present, don't check reviews if hotel already present, for faster re-crawling")
    parser.add_argument(
        "--hotel_only",
        action="store_true",
        help="if option present, don't check reviews for hotel either way"
    )
    parser.add_argument(
        "--update_existing",
        action="store_true",
        help="if option present, update existing hotel entry instead of skipping."
    )
    args = parser.parse_args()

    logger = setuplogger(loggername="Main Manager")
    logger.info("Main Booking Manager arguments = [{0}]".
        format(str(sys.argv)))

    if not args.file:
        parser.print_help()
    else:
        crawl_manager = WikitravelManager()
        crawl_manager.crawl_attraction(
            filepath=args.file,
            skip_flag=args.skip,
            hotel_only=args.hotel_only,
            update_existing=args.update_existing)
