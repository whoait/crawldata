"""
TripadvisorManager to manage crawling flow
"""
from selenium import webdriver
from BeautifulSoup import BeautifulSoup
import pymongo
import requests, requests.exceptions
import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from .crawler import TripadvisorCrawler
from ..data.attraction import Attraction
from ..data.entitysource import EntitySource
from ..base.manager import BaseManager
from ..data.review import Review
from .parse_hotel import TripadvisorHotel
from .parse_attraction import TripadvisorAttraction
from .parse_review import TripadvisorReview
from .util import get_site_id
from ..string_util import setuplogger

class TripadvisorManager(BaseManager):
    def __init__(self):
        self.logger = setuplogger(loggername="Tripadvisor Manager")
        self.driver_options = webdriver.chrome.options.Options()
        self.driver_options.add_argument("-incognito")
        self.driver = webdriver.Firefox()
        self.conn = pymongo.MongoClient()
        self.mongodb = self.conn['hotel_crawler']
        self.crawler = TripadvisorCrawler("http://www.tripadvisor.com")

    def __del__(self):
        self.driver.quit()
        self.conn.disconnect()

    def reload_driver(self):
        # to handle firefox memory leakage, reload the driver after each entity source
        self.driver.quit()
        self.driver = webdriver.Firefox()

    def crawl_attractions(self, filepath=None, skip_flag=False, hotel_only=False, update_existing=False):
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
                        if update_existing or not self.mongodb.attraction.find_one({
                                "source_entity_id": get_site_id(attraction_url, "-d"),
                                "source": "Tripadvisor"}):
                            self.logger.info("parsing attraction url = {0}".format(attraction_url))
                            attraction = Attraction()
                            attraction.set_city(
                                place_dict['city'],
                                place_dict['country'])
                            attraction_parser = TripadvisorAttraction(
                                self.driver,
                                attraction_url)
                            attraction.parse(attraction_parser)
                            attraction.write(self.mongodb, update=True)
                        else:
                            self.logger.info(
                                "seen attraction {0}".format(attraction_url))
                            # if skip - continue and don't search for more reviews
                            if skip_flag:
                                continue
                        # we don't need reviews if listing/hotel_only
                        if hotel_only:
                            continue
                        # crawl reviews
                        counter = 0
                        #review_url = attraction_url.replace(
                        #    '-{0}.html'.format(place_dict['url_separator']),
                        #    '-or{0}-{1}.html'.format(counter, place_dict['url_separator']))
                        review_url = attraction_url

                        requests_counter = 0
                        while requests_counter < 3:
                            try:
                                r = requests.get(review_url)
                                break
                            except requests.exceptions.ConnectionError:
                                requests_counter += 1
                                continue
                        if requests_counter == 3:
                            # go find reviews for another attraction.
                            break

                        self.logger.info("review url = {0}, type = {1}".format(r.url, type(r.url)))
                        self.reload_driver()
                        while r.url == review_url:
                            self.driver.get(r.url)
                            review_list_soup = BeautifulSoup(
                                self.driver.page_source
                            )
                            review_div_soup = review_list_soup.find(id='REVIEWS')
                            if not review_div_soup:
                                break
                            review_list = review_list_soup.find(id='REVIEWS').findAll("div", "reviewSelector")
                            for review_entry in review_list:
                                # parse each review
                                review_parser = TripadvisorReview(
                                    self.driver,
                                    attraction_url,
                                    review_entry
                                )
                                review_id = review_parser.review_id
                                if not self.mongodb.review.find_one({
                                        "site_id": review_id,
                                        "source": "Tripadvisor"
                                        }):
                                    review = Review()
                                    review.parse(review_parser)
                                    review.write(self.mongodb)
                                else:
                                    self.logger.info(
                                        "seen review {0}".format(review_id))
                            counter += 10
                            review_url = attraction_url.replace(
                                '-Reviews-',
                                '-Reviews-or{0}-'.format(counter))

                            requests_counter = 0
                            while requests_counter < 3:
                                try:
                                    r = requests.get(review_url)
                                    break
                                except requests.exceptions.ConnectionError:
                                    requests_counter += 1
                                    continue
                            if requests_counter == 3:
                                # go find reviews for another attraction.
                                break

                        self.logger.info("url mismatch - r.url = {0}, review_url = {1}")

    def crawl(self, filepath=None):
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

                    for hotel_url in hotel_url_list:
                        # continue if id can be matched
                        if not self.mongodb.entitysource.find_one({
                            "source_entity_id":
                            get_site_id(hotel_url, "-d"),
                            "source":
                            "Tripadvisor"}):
                            # reload driver after each hotel - takes about 10 s
                            self.reload_driver()
                            self.logger.info("parsing hotel url: {0}".format(hotel_url))
                            # find details on a hotel
                            hotel = EntitySource()
                            hotel.set_city(
                                place_dict['city'],
                                place_dict['country'])
                            hotel_parser = TripadvisorHotel(
                                self.driver,
                                hotel_url)
                            hotel.parse(hotel_parser)
                            hotel.write(self.mongodb)
                            self.logger.info(
                                "parsed hotel {0} from url {1}".
                                format(
                                    hotel,
                                    hotel_url))
                        # we still need to crawl new hotel reviews if hotel exists
                        else:
                            self.logger.info(
                                "seen hotel = {0}".
                                format(hotel_url))
                        # find all reviews of a hotel
                        review_url_list = self.crawler.crawl_reviews(
                            hotel_url,
                            place_dict)

                        for review_url in review_url_list:
                            if not self.mongodb.review.find_one({
                                "site_id":
                                get_site_id(review_url, "-r"),
                                "source":
                                "Tripadvisor"}):
                                review = Review()
                                review_parser = TripadvisorReview(
                                    self.driver,
                                    review_url)
                                review.parse(review_parser)
                                review.write(self.mongodb)
                                self.logger.info(
                                    "parsed review {0} from url {1} on hotel {2}".
                                    format(
                                        review,
                                        review_url,
                                        hotel_url))
                        else:
                            self.logger.info(
                                "seen review {0}".
                                format(review_url))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="crawls listing information from TripAdvisor.com")
    parser.add_argument(
        "--file",
        help="file path of text file containing urls to parse")
    parser.add_argument(
        "--skip",
        action="store_true",
        help="if option present, don't check reviews if listing already present, for faster re-crawling")
    parser.add_argument(
        "--hotel_only",
        action="store_true",
        help="if option present, don't check reviews for listing either way"
    )
    parser.add_argument(
        "--update_existing",
        action="store_true",
        help="if option present, update existing listing entry instead of skipping."
    )
    args = parser.parse_args()

    logger = setuplogger(loggername="Main Manager")
    logger.info("Main Tripadvisor Manager arguments = [{0}]".
                format(str(sys.argv)))

    if not args.file:
        parser.print_help()
    else:
        crawl_manager = TripadvisorManager()
        crawl_manager.crawl_attractions(
            filepath=args.file,
            skip_flag=args.skip,
            hotel_only=args.hotel_only,
            update_existing=args.update_existing)

    # main()
