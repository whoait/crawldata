# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from crawl.models import CityWeatherMonth
from scrapy.contrib.djangoitem import DjangoItem


class TheBestTimeToVisitItem(DjangoItem):
    django_model = CityWeatherMonth
