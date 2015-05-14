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

from .crawler import VirtualtouristCrawler
from ..data.entitysource import EntitySource
from ..base.manager import BaseManager
from ..data.review import Review
from .parse_hotel import VirtualtouristHotel
from .parse_review import VirtualtouristReview
from .util import get_site_id, trim_url_query_string
from ..string_util import setuplogger


class VirtualtouristManager(BaseManager):
    def __init__(self):
        self.logger = setuplogger(loggername="Virtualtourist Manager")
        self.driver = None # init later
        self.conn = pymongo.MongoClient()
        self.mongodb = self.conn['hotel_crawler']
        self.crawler = VirtualtouristCrawler("http://www.virtualtourist.com", self.mongodb)

    def __del__(self):
        # self.driver.quit()
        self.conn.disconnect()

    def reload_driver(self):
        # no complex js, requests module is good enough
        pass

    def crawl(self, filepath=None, skip_flag=False, hotel_only=False, update_existing=False):
        # each entry is place list will have a {url, cityID, city, full_name, country}
        if filepath:
            with open(filepath, "r") as f:
                for line in f:
                    place_dict = json.loads(line)
                    self.logger.info(
                        "loaded place_dict = {0}".
                        format(str(place_dict)))
                    # find all hotel urls in a city
                    hotel_url_list = self.crawler.crawl_hotels(
                        place_dict['url'],
                        place_dict)

                    url_index = 0
                    for hotel_dict in hotel_url_list:
                        self.logger.info("Seen hotel {0}".format(url_index))
                        url_index += 1
                        hotel_parser = VirtualtouristHotel(
                            None,
                            hotel_dict['url'],
                            hotel_dict)
                        # continue if id can be matched
                        if update_existing or not self.mongodb.entitysource.find_one({
                            "source_entity_id":
                            hotel_dict['hotel_id'],
                            "source":
                            "Virtualtourist"}):

                            self.logger.info("parsing hotel url: {0}".format(hotel_dict))
                            # find details on a hotel
                            hotel = EntitySource()
                            hotel.set_city(
                                place_dict['city'],
                                place_dict['country'])
                            hotel.parse(hotel_parser)
                            hotel.write(self.mongodb, update_existing)
                            self.logger.info(
                                "parsed hotel {0} from url {1}".
                                format(
                                    hotel,
                                    hotel.website))
                        # we still need to crawl new hotel reviews if hotel exists
                        else:
                            self.logger.info(
                                "seen hotel = {0}".
                                format(hotel_dict['url']))

                            # if skip - continue and don't search for more reviews
                            if skip_flag:
                                continue

                        if hotel_only:
                            continue

                        # find all reviews of a hotel
                        place_dict['hotel_id'] = hotel_dict['hotel_id']

                        max_review_count = hotel_parser.parse_review_count()
                        step_size = 15
                        review_url_list = self.crawler.crawl_reviews(
                            hotel_dict['url'],
                            {'review_count': (max_review_count + step_size - 1)/step_size})

                        driver = None

                        for url in review_url_list:

                            self.logger.info("parsing review_list with review_search_url = {0}".format(url))
                            # we need webdriver Firefox because cookies
                            review_soup = BeautifulSoup(
                                requests.get(url).text
                            )

                            if review_soup.find(id="vtReviews"):
                                for one_review_soup in review_soup.find(id="vtReviews").findAll("div", "vt-review media"):
                                    # need to initialize parser to allow extraction of review_id
                                    parse_review = VirtualtouristReview(
                                        None,
                                        url,
                                        one_review_soup,
                                        hotel_dict['hotel_id']
                                    )

                                    if not self.mongodb.review.find_one({
                                            "site_id": parse_review.parse_site_id(),
                                            "source": "Virtualtourist"}):
                                        review = Review()
                                        review.parse(parse_review)
                                        review.write(self.mongodb)
                                        self.logger.info(
                                            "parsed review {0} from url {1} on hotel {2}".
                                            format(
                                                parse_review.parse_site_id(),
                                                hotel_dict['url'],
                                                hotel_dict['hotel_id']
                                            ))
                                    else:
                                        self.logger.info(
                                            "seen review {0}".
                                            format(parse_review.parse_site_id()))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="crawls hotel information from Virtualtourist.com")
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
    logger.info("Main Virtualtourist Manager arguments = [{0}]".
        format(str(sys.argv)))

    if not args.file:
        parser.print_help()
    else:
        crawl_manager = VirtualtouristManager()
        crawl_manager.crawl(
            filepath=args.file,
            skip_flag=args.skip,
            hotel_only=args.hotel_only,
            update_existing=args.update_existing)

    # main()
