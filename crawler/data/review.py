"""
Base Review class
"""
import string
import pymongo
import bson
import math
import logging
from .base import Baseclass
from ..string_util import setuplogger

class Review(Baseclass):

    #fields
    source = None
    title = None
    user_id = None
    site_id = None
    username = None
    place_from = None
    helpful = None
    date = None
    review_text = None
    review_positive = None
    review_negative = None
    entity_source_id = None
    review_rating = {}

    def __init__(self):
        super(Review, self).__init__()

    def parse(self, parser):
        self.source = parser.parse_source()
        self.title = parser.parse_title()
        self.site_id = parser.parse_site_id()
        self.username = parser.parse_username()
        self.user_id = parser.parse_user_id()
        self.place_from = parser.parse_place_from()
        self.helpful = parser.parse_helpful()
        self.date = parser.parse_date()
        self.review_text = parser.parse_review_text()
        self.review_positive = parser.parse_review_positive()
        self.review_negative = parser.parse_review_negative()
        self.entity_source_id = parser.parse_entity_source_id()
        self.review_rating = parser.parse_review_rating()
        #self.review_categories = parser.parse_review_categories()

    def write(self, mongodb):
        try:
            mongodb.review.insert({
                'source': self.source,
                'title': self.title,
                'site_id': self.site_id,
                'user_id' : self.user_id,
                'username': self.username,
                'place_from': self.place_from,
                'helpful': self.helpful,
                'date': self.date,
                'review_text': self.review_text,
                'review_positive': self.review_positive,
                'review_negative': self.review_negative,
                'entity_source_id': self.entity_source_id,
                'review_rating': self.review_rating,
                #'review_categories': self.review_categories
                })
        except Exception, e:
            self.logger.exception(e)

    def __repr__(self):
        return "[{0}:({1}):{2}]:{3} on {4}".format(
            self.source,
            self.site_id,
            self.username,
            self.title,
            self.date).encode("ascii", "ignore")

