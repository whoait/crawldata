"""
TripadvisorManager to manage crawling flow
"""
from selenium import webdriver
import pymongo
import os
import json
import urllib2
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


from BeautifulSoup import BeautifulSoup


from .crawler import AgodaCrawler
from ..data.entitysource import EntitySource
from ..base.manager import BaseManager
from ..data.review import Review
from .parse_hotel import AgodaHotel
from .parse_review import AgodaReview
from .util import get_site_id 
from ..string_util import setuplogger


class AgodaManager(BaseManager):
    def __init__(self):
        self.logger = setuplogger(loggername="Agoda Manager")
        self.driver = webdriver.Firefox()
        self.conn = pymongo.MongoClient()
        self.mongodb = self.conn['hotel_crawler']
        self.crawler = AgodaCrawler("http://www.agoda.com")

    def __del__(self):
        self.driver.quit()
        self.conn.disconnect()

    def reload_driver(self):
        # to handle firefox memory leakage, reload the driver after each entity source
        self.driver.quit()
        self.driver = webdriver.Firefox()

    def crawl(self, filepath=None, skip=False):
        # each entry is place list will have a {url, cityID, city, full_name, country}
        self.logger.info("crawling with filepath = {0}, skip = {1}".
            format(filepath, skip))
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
                        hotel_id = 0
                        # continue if id can be matched
                        if not self.mongodb.entitysource.find_one({
                            "website":
                            hotel_url,
                            "source":
                            "Agoda"}):
                            # quit driver after each hotel - takes about 10 s
                            self.driver = webdriver.Firefox()
                            self.logger.info("parsing hotel url: {0}".format(hotel_url))
                            # find details on a hotel
                            hotel = EntitySource()
                            hotel.set_city(
                                place_dict['city'],
                                place_dict['country'])
                            hotel_parser = AgodaHotel(
                                self.driver,
                                hotel_url)
                            hotel.parse(hotel_parser)
                            hotel.write(self.mongodb)
                            hotel_id = hotel.source_entity_id
                            self.logger.info(
                                "parsed hotel {0} from url {1}".
                                format(
                                    hotel,
                                    hotel_url))
                            self.driver.quit()
                        # we still need to crawl new hotel reviews if hotel exists
                        else:
                            hotel_id = self.mongodb.entitysource.find_one({
                                "website": hotel_url,
                                "source": "Agoda"},
                                {'_id': 0, 'source_entity_id': 1})['source_entity_id']
                            self.logger.info(
                                "seen hotel = {0}".
                                format(hotel_url))
                            if skip:
                                continue
                        # find all reviews of a hotel
                        # need to obtain real hotel_url by going to hotel

                        hotel_native_url = urllib2.urlopen(hotel_url).geturl().split('?')[0]
                        hotel_review_url = hotel_native_url.replace(
                            '/hotel/',
                            '/reviews/')
                        # review_url_list = self.crawler.crawl_reviews(
                        #    hotel_review_url,
                        #    place_dict)

                        page_count = 1
                        try_count = 0
                        while True:
                            if page_count == 1:
                                review_url = hotel_review_url
                            else:
                                review_url = hotel_review_url.replace(
                                    "/reviews/",
                                    "/reviews-page-{0}/".format(page_count))

                            self.logger.info("parsing review url - {0}".format(review_url))
                            # we need to extract soup and
                            # feed it to the review parser
                            # self.driver.get(review_url)
                            try:
                                review_page_soup = BeautifulSoup(
                                    urllib2.urlopen(review_url).read()
                                )
                            except urllib2.HTTPError:
                                try_count += 1
                                if try_count == 3:
                                    break
                                else:
                                    continue
                            review_table_soup = review_page_soup.find(
                                "table", "hotelreviewlist")
                            # deal with unreliable connections
                            if not review_table_soup:
                                self.logger.info("Cannot find review table for url = {0}".
                                    format(review_url))
                            try_count = 0
                            counter = 1
                            for one_review_soup in review_table_soup.findAll("tr"):
                                id_index = counter
                                self.logger.info("parsing review with url = {0}, id_index = {1}".
                                    format(review_url, id_index))
                                one_review = AgodaReview(
                                    self.driver,
                                    review_url,
                                    one_review_soup,
                                    hotel_id,
                                    id_index)
                                review_id = one_review.review_id

                                if not self.mongodb.review.find_one({
                                    "site_id": review_id,
                                    "source": "Agoda"
                                }):
                                    review = Review()
                                    review_parser = AgodaReview(
                                        self.driver,
                                        review_url,
                                        one_review_soup,
                                        hotel_id,
                                        id_index)
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
                                counter += 1
                            page_count += 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="crawls hotel information from Agoda")
    parser.add_argument(
        "--file",
        help="file path of text file containing urls to parse")
    parser.add_argument(
        "--skip",
        action="store_true",
        help="if option present, don't check reviews if hotel already present, for faster re-crawling")
    args = parser.parse_args()

    logger = setuplogger(loggername="Main Manager")
    logger.info("Main Agoda Manager arguments = [{0}]".
        format(str(sys.argv)))

    if not args.file:
        parser.print_help()
    else:
        crawl_manager = AgodaManager()
        crawl_manager.crawl(filepath=args.file, skip=args.skip)

    """
    logger = setuplogger(loggername="Main Manager")
    logger.info("Main Agoda Manager arguments = [{0}]".
        format(str(sys.argv)))
    if len(sys.argv) >= 2:
        if (sys.argv[1] == "--help" or
            sys.argv[1] == "-h"):
            print ("Enter ./manager.py --file "
                "<file_path of text file containing urls to parse>")
        elif (sys.argv[1] == "--file" or
            sys.argv[1] == "-f"):
            # parse filename next
            crawl_manager = AgodaManager()
            crawl_manager.crawl(filepath=sys.argv[2])
    else:
        print ("Enter ./manager.py --file "
            "<file_path of text file containing urls to parse>")
    """
    # main()
