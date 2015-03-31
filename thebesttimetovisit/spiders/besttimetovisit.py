import urllib
import logging
from scrapy.spider import Spider
from scrapy import Selector
from scrapy.http.request import Request
from scrapy.http import TextResponse
from thebesttimetovisit.items import TheBestTimeToVisitItem
from thebesttimetovisit.pipelines import TheBestTimeToVisitPipeline
from crawl.models import City, CityWeatherMonth

def month_to_num(month):

    return{
            'january'   : 1,
            'february'  : 2,
            'march'     : 3,
            'april'     : 4,
            'may'       : 5,
            'june'      : 6,
            'july'      : 7,
            'august'    : 8,
            'september' : 9,
            'october'   : 10,
            'november'  : 11,
            'december'  : 12
    }[month]


# run this command : python manage.py scrapy crawl thebesttimetovisit
class TheBestTimeToVisitSpider(Spider):
    name = "thebesttimetovisit"
    allowed_domains = ["thebesttimetovisit.com"]
    start_urls = []

    counter = 0
    max_page = 100000

    using_log = False
    logger = None

    def __init__(self, name=None, url=None, **kwargs):
        if url:
            if name is not None:
                self.name = name
            elif not getattr(self, 'name', None):
                raise ValueError("%s must have a name" % type(self).__name__)
            self.__dict__.update(kwargs)
            self.start_urls = [url]
        else:
            # If there is no specific URL get it from Database
            wikiliks = None # < -- CODE TO RETRIEVE THE LINKS FROM DB -->
            if wikiliks == None:
                wikiliks = [
                    "http://www.thebesttimetovisit.com/weather/bangkok-idvilleeng-93.html"
                ]
                # print "**************************************"
                # print "No Links to Query"
                # print "**************************************"
                # return None

            # print 'dasdasdas'
            # print wikiliks
            for link in wikiliks:
                # print link
                # print urllib.unquote_plus(link)
                # print "===="
                # SOME PROCESSING ON THE LINK GOES HERE
                self.start_urls.append(urllib.unquote_plus(link))

    def init_logger(self):
        log_file = '/var/tmp/cron_foursquare.log'
        print 'Writing log into file %s ...' % log_file
        self.logger = logging.getLogger('cron_foursquare')

        hdlr = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)

        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.WARNING)

    def _print(self, s):
        if self.using_log:
            self.logger.info(s)
        else:
            print s.encode('utf-8')

    def parse(self, response):
        self.counter += 1
        errors = []
        base_url = "http://www.thebesttimetovisit.com"
        hxs = Selector(response)

        posts = hxs.xpath('//table[@cellpadding="2"]/tr')

        if posts:
            del posts[0]

        # TODO: find a way to know which city that we're crawling data, now 293916 is Bangkok in main_city
        city = City.objects.get(id=293916)
        for post in posts:
            rows = post.xpath('td/text()').extract()
            item = CityWeatherMonth()
            month = rows[0]
            item.city = city
            item.month = month_to_num(month)
            item.sunlight = rows[1]
            item.average_min = rows[2]
            item.average_max = rows[3]
            item.record_min = rows[4]
            item.record_max = rows[5]
            item.precipitations = rows[6]
            item.wet_days = rows[7]
            try:
                item.full_clean()
            except Exception as e:
                errors.append('City %s . Month: %s' % (city, month))
            else:
                item.save()

        self._print('Errors (%s): ' % len(errors))
        for error in errors:
            self._print('- %s' % error)