"""
TripadvisorManager to manage crawling flow
"""
from selenium import webdriver
from BeautifulSoup import BeautifulSoup
import requests
import pymongo
import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from .crawler import ExpediaCrawler
from ..data.entitysource import EntitySource
from ..base.manager import BaseManager
from ..data.review import Review
from .parse_hotel import ExpediaHotel
from .parse_review import ExpediaReview
from .util import get_site_id, trim_url_query_string
from ..string_util import setuplogger


class ExpediaManager(BaseManager):
    def __init__(self):
        self.logger = setuplogger(loggername="Expedia Manager")
        self.driver = None # init later
        self.conn = pymongo.MongoClient()
        self.mongodb = self.conn['hotel_crawler']
        self.crawler = ExpediaCrawler("http://www.expedia.com")

    def __del__(self):
        # self.driver.quit()
        self.conn.disconnect()

    def reload_driver(self):
        # no complex js, requests module is good enough
        pass

    def crawl(self, filepath=None, skip_flag=False):
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
                    for hotel_url in hotel_url_list:
                        self.logger.info("Seen hotel {0}".format(url_index))
                        url_index += 1
                        # continue if id can be matched
                        if not self.mongodb.entitysource.find_one({
                            "source_entity_id":
                            get_site_id(hotel_url),
                            "source":
                            "Expedia"}):
                            self.driver = webdriver.Firefox()
                            self.logger.info("parsing hotel url: {0}".format(hotel_url))
                            # find details on a hotel
                            hotel = EntitySource()
                            hotel.set_city(
                                place_dict['city'],
                                place_dict['country'])
                            hotel_parser = ExpediaHotel(
                                self.driver,
                                hotel_url)
                            hotel.parse(hotel_parser)
                            hotel.write(self.mongodb)
                            self.logger.info(
                                "parsed hotel {0} from url {1}".
                                format(
                                    hotel,
                                    hotel.website))
                            self.driver.quit()
                        # we still need to crawl new hotel reviews if hotel exists
                        else:
                            self.logger.info(
                                "seen hotel = {0}".
                                format(hotel_url))
                            # if skip - continue and don't search for more reviews
                            if skip_flag:
                                continue

                        # find all reviews of a hotel
                        place_dict['hotel_id'] = get_site_id(hotel_url)
                        # max_review_page = self.crawler.crawl_reviews(hotel_url, place_dict)
                        counter = 0
                        # for counter in xrange(0, max_review_page):
                        fail_count = 0
                        while True:
                            review_search_url = place_dict['review_url']
                            review_search_url += "{0}/?_type=json".format(get_site_id(hotel_url))
                            review_search_url += "&start={0}&items=10&sortBy=&categoryFilter=&languageFilter=&languageSort=en".format(counter)

                            try:
                                review_dict = requests.get(review_search_url).json()
                            except:
                                fail_count += 1
                                self.logger.info("cannot retrieve resource for url= {0}".format(review_search_url))
                                continue
                            # get actual lists of reviews
                            review_count = review_dict['reviewDetails']['numberOfReviewsInThisPage']
                            if review_count == 0:
                                break
                            try:
                                review_list = review_dict['reviewDetails']['reviewCollection']['review']
                            except:
                                self.logger.error("no review dictionary from valid review search range for {0} on hotel {1}".
                                    format(review_search_url, hotel_url))
                            self.logger.info("crawling {0} reviews in url = {1}".
                                             format(review_count,
                                                    review_search_url))
                            for review_entry in review_list:
                                # filter out non-expedia reviews
                                if review_entry['brandType'] != "Expedia":
                                    continue
                                # filter out non-english reviews
                                if not review_entry['contentLocale'].startswith("en"):
                                    continue
                                if not self.mongodb.review.find_one({
                                        "site_id": review_entry['reviewId'],
                                        "source": "Expedia"}):
                                    review = Review()
                                    parse_review = ExpediaReview(
                                        self.driver,
                                        review_search_url,
                                        None,
                                        review_entry
                                    )
                                    review.parse(parse_review)
                                    review.write(self.mongodb)
                                    self.logger.info(
                                        "parsed review {0} from url {1} on hotel {2}".
                                        format(
                                            review,
                                            review_entry['reviewId'],
                                            hotel_url))

                                else:
                                    self.logger.info(
                                        "seen review {0}".
                                        format(review_entry['reviewId']))
                            counter += review_count


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="crawls hotel information from Expedia")
    parser.add_argument(
        "--file",
        help="file path of text file containing urls to parse")
    parser.add_argument(
        "--skip",
        action="store_true",
        help="if option present, don't check reviews if hotel already present, for faster re-crawling")
    args = parser.parse_args()

    logger = setuplogger(loggername="Main Manager")
    logger.info("Main Expedia Manager arguments = [{0}]".
        format(str(sys.argv)))

    if not args.file:
        parser.print_help()
    else:
        crawl_manager = ExpediaManager()
        crawl_manager.crawl(filepath=args.file, skip_flag=args.skip)

    # main()