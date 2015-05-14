"""
Base EntitySource class
"""
import string
import pymongo
import math
import logging
from .base import Baseclass
from ..string_util import setuplogger

class EntitySource(Baseclass):

    #fields
    source = None
    source_entity_id = None
    name = None
    address = None
    postcode = None
    lat = None
    lng = None
    city = None
    country = None
    category = None
    email = None
    website = None
    phone = None
    description = None
    short_description = None
    avatar = None
    entity_source_rating = {}
    all_photos = []
    amenity = {}

    def __init__(self):
        super(EntitySource, self).__init__()

    def set_city(self, city, country):
        self.city = city
        self.country = country

    def parse(self, parser):
        self.source = parser.parse_source()
        self.source_entity_id = parser.parse_source_entity_id()
        self.name = parser.parse_name()
        self.address = parser.parse_address()
        self.postcode = parser.parse_postcode()
        self.lat = parser.parse_lat()
        self.lng = parser.parse_lng()
        #self.city = parser.parse_city()
        #self.country = parser.parse_country()
        self.category = parser.parse_category()
        self.email = parser.parse_email()
        self.website = parser.parse_website()
        self.phone = parser.parse_phone()
        self.description = parser.parse_description()
        self.short_description = parser.parse_short_description()
        self.avatar = parser.parse_avatar()
        self.stars = parser.parse_stars()
        self.entity_source_rating = parser.parse_entity_source_rating()
        self.all_photos = parser.parse_all_photos()
        self.amenity = parser.parse_amenity()

    def write(self, mongodb, update=False):
        try:
            entitysource_dict = {
                'source': self.source,
                'source_entity_id': self.source_entity_id,
                'name': self.name,
                'address': self.address,
                'postcode': self.postcode,
                'lat': self.lat,
                'lng': self.lng,
                'city': self.city,
                'country': self.country,
                'category': self.category,
                'email': self.email,
                'website': self.website,
                'phone': self.phone,
                'description': self.description,
                'short_description': self.short_description,
                'all_photos': self.all_photos,
                'avatar': self.avatar,
                'stars': self.stars or 0,
                'entity_source_rating': self.entity_source_rating,
                'amenity': self.amenity}
            if update:
                mongodb.entitysource.update(
                    {"source_entity_id": self.source_entity_id},
                    {"$set": entitysource_dict},
                    upsert=True
                )
            else:
                mongodb.entitysource.insert(entitysource_dict)
        except Exception, e:
            self.logger.exception(e)

    def __repr__(self):
        return "[{0}:({1}):{2}]".format(
            self.source,
            self.source_entity_id,
            self.name
            )

