# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from crawl.models import CityWeatherMonth
from scrapy.exceptions import DropItem
from items import TheBestTimeToVisitItem

class TheBestTimeToVisitPipeline(object):

    def process_item(self, item, spider):
        print 'pipline'
        print item
        try:
            item.full_clean()
        except Exception as e:
            print e
        else:
            item.save()
        return item