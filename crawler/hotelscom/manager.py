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

from .crawler import HotelscomCrawler
from ..data.entitysource import EntitySource
from ..base.manager import BaseManager
from ..data.review import Review
from .parse_hotel import HotelscomHotel
from .parse_review import HotelscomReview
from .util import get_site_id 
from ..string_util import setuplogger


class HotelscomManager(BaseManager):
    def __init__(self):
        self.logger = setuplogger(loggername="Hotelscom Manager")
        self.driver = webdriver.Firefox()
        self.conn = pymongo.MongoClient()
        self.mongodb = self.conn['hotel_crawler']
        self.crawler = HotelscomCrawler("http://www.hotels.com")

    def __del__(self):
        self.driver.quit()
        self.conn.disconnect()

    def reload_driver(self):
        # no complex js, requests module is good enough
        pass

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
                            get_site_id(hotel_url),
                            "source":
                            "Hotelscom"}):

                            self.logger.info("parsing hotel url: {0}".format(hotel_url))
                            # find details on a hotel
                            hotel = EntitySource()
                            hotel.set_city(
                                place_dict['city'],
                                place_dict['country'])
                            hotel_parser = HotelscomHotel(
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

                        # find all reviews of a hotelcomplaints
                        place_dict['hotel_id'] = get_site_id(hotel_url)
                        review_url_list = self.crawler.crawl_reviews(
                            hotel_url,
                            place_dict)

                        for review_url in review_url_list:
                            # iterate through up to 50 reviews per review_url
                            self.logger.info("Getting review from url = {0}".format(review_url))
                            review_soup = BeautifulSoup(requests.get(review_url)._content)
                            # review id needs to be manually constructed

                            review_list_soup = (list(
                                review_soup.find("div", "reviews").
                                findAll("div", "review"))
                                                if review_soup.find("div", "reviews")
                                                else [])
                            for one_review_soup in review_list_soup:
                                one_review = HotelscomReview(self.driver,
                                                             review_url,
                                                             one_review_soup)
                                # exclude reviews not from hotels.com
                                if not one_review.parse_origin():
                                    continue
                                review_site_id = one_review.build_review_id()

                                if not self.mongodb.review.find_one({
                                    "site_id": review_site_id,
                                    "source": "Hotelscom"}):
                                    review = Review()
                                    review.parse(one_review)
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
    logger = setuplogger(loggername="Main Manager")
    logger.info("Main Hotelscom Manager arguments = [{0}]".
        format(str(sys.argv)))
    if len(sys.argv) >= 2:
        if (sys.argv[1] == "--help" or
            sys.argv[1] == "-h"):
            print ("Enter ./manager.py --file "
                "<file_path of text file containing urls to parse>")
        elif (sys.argv[1] == "--file" or
            sys.argv[1] == "-f"):
            # parse filename next
            crawl_manager = HotelscomManager()
            crawl_manager.crawl(filepath=sys.argv[2])
    else:
        print ("Enter ./manager.py --file "
            "<file_path of text file containing urls to parse>")
    # main()
