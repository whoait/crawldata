import logging
import urlparse
from scrapy.spider import Spider
from scrapy import Selector
from crawl.models import City, Country, CityWeatherMonth, CrawlDetail

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
            # wikiliks = None # < -- CODE TO RETRIEVE THE LINKS FROM DB -->
            wikiliks = CrawlDetail.objects.filter(data_type_name=CrawlDetail.MONTH_WEATHER_INFO)
            if wikiliks == None:
                print "**************************************"
                print "No Links to Query"
                print "**************************************"
                return None

            for link in wikiliks:
                # SOME PROCESSING ON THE LINK GOES HERE
                content_type = link.content_type
                object_id = link.object_id
                url = link.source_url
                url += '?content_type=%s&object_id=%s' % (content_type, object_id)
                # print url
                self.start_urls.append(url)
                # self.start_urls.append(link.source_url)

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
        par = urlparse.parse_qs(urlparse.urlparse(response.url).query)
        object_id       = par['object_id'][0]
        content_type    = par['content_type'][0]

        if content_type == 'city':
            cls = City
        if content_type == 'country':
            cls = Country
        object = cls.objects.get(id=object_id)

        self._print('Staring crawl from (%s) ....: ' % response.url)

        for post in posts:
            rows = post.xpath('td/text()').extract()
            month = month_to_num(rows[0])

            try:
                weather = CityWeatherMonth.objects.get(city=object, month=month)
            except CityWeatherMonth.DoesNotExist:
                weather = None

            if weather:
                item = weather
            else:
                item = CityWeatherMonth()
                item.city = object
                item.month = month

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
                errors.append('Errors message : %s . [%s %s . Month: %s]' % (str(e), content_type, object, month))
            else:
                item.save()
                self._print('Added %s : %s' % (item.city, item.month))

        if len(errors) == 0:
            self._print('Crawling sucessful %s' % len(posts))
        else:
            self._print('Errors (%s): ' % len(errors))
            for error in errors:
                self._print('- %s' % error)