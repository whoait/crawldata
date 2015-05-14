__author__ = 'zong'
import pymongo
import requests
import re
from BeautifulSoup import BeautifulSoup


conn = pymongo.MongoClient()
db = conn['hotel_crawler']
prog = re.compile(
            "(Review_id=[0-9]+)(?P<sentence>[a-zA-Z0-9_ .,!?']+)")
# fix missing hotel info

# 1 - hotel names
for hotel in db.entitysource.find({
    'source': 'Agoda'
}):
    # we need to retrieve
    hotel_soup = BeautifulSoup(requests.get(hotel['website']).text)
    title_soup = hotel_soup.find(
        id="ctl00_ctl00_MainContent_ContentMain_HotelHeaderHD_lblHotelName")
    if title_soup:
        hotel_name = title_soup.text.strip()
        db.entitysource.update(
            {'_id': hotel['_id']},
            {'$set': {'name': hotel_name}})

# fix missing review data
# 1 - clean title
for review in db.review.find({
    'source': 'Agoda'
}):
    old_title = review.get('title')
    if old_title:
        result = prog.match(old_title)
        title = result.group('sentence')
        db.review.update(
            {'_id': review['_id']},
            {'$set': {'title': title}}
        )
    else:
        print "no title for review - {0}".format(review)