import urlparse
import json
import logging
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


# run this command : python manage.py scrapy crawl sunrisesunset
class TheBestTimeToVisitSpider(Spider):
    name = "sunrisesunset"
    allowed_domains = ["sunrisesunset.com"]
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
            wikiliks = CrawlDetail.objects.filter(data_type_name=CrawlDetail.MONTH_ALMANAC_INFO)
            if wikiliks == None:
                # wikiliks=[
                #     'http://www.sunrisesunset.com/calendar.asp?comb_city_info=Seoul,%20South%20Korea;-126.978;37.5665;9;0&want_mphase=1&month=5&year=2015&time_type=1',
                # ]
                print "**************************************"
                print "No Links to Query"
                print "**************************************"
                return None

            for link in wikiliks:
                # SOME PROCESSING ON THE LINK GOES HERE
                content_type = link.content_type
                object_id = link.object_id
                for i in range(0, 12):
                    url = link.source_url
                    url += '&month=%s&content_type=%s&object_id=%s' % (i+1, content_type, object_id)
                    # print url
                    self.start_urls.append(url)

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

    def _averageTime(self, timeList):
        total_hours = 0
        total_mins  = 0

        for tm in timeList:
            time_parts = [int(s) for s in tm.split(':')]
            total_hours += time_parts[0]
            total_mins += time_parts[1]

        average_hours = total_hours/len(timeList)
        average_mins = total_mins/len(timeList)

        return "%d:%02d" % (average_hours, average_mins)

    def parse(self, response):
        self.counter += 1
        errors = []
        base_url = "http://www.sunrisesunset.com"
        hxs = Selector(response)

        posts = hxs.xpath('(//table)[1]/tr/td[@valign="top"]/font[@size="1"]')

        # TODO: find a way to know which city that we're crawling data, now 293916 is Bangkok in main_city
        par = urlparse.parse_qs(urlparse.urlparse(response.url).query)
        object_id       = par['object_id'][0]
        month           = par['month'][0]
        content_type    = par['content_type'][0]

        sunrise_list        = []
        sunset_list         = []
        sunrise_time_list   = []
        sunset_time_list    = []

        if content_type == 'city':
            cls = City
        if content_type == 'country':
            cls = Country
        object = cls.objects.get(id=object_id)

        for post in posts:
            sunrise = post.xpath('./br[1]/following-sibling::text()[1]').extract()[0]
            sunrise_list.append(sunrise)
            sunrise_time_list.append(sunrise.split(' ')[1])
            sunset = post.xpath('./br[2]/following-sibling::text()[1]').extract()[0]
            sunset_list.append(sunset)
            sunset_time_list.append(sunset.split(' ')[1])

        if sunrise_time_list:
            sunrise_average = self._averageTime(sunrise_time_list)
        if sunset_time_list:
            sunset_average = self._averageTime(sunset_time_list)

        detail = json.dumps(
            {
                'sunrise'   : json.dumps(sunrise_list),
                'sunset'    : json.dumps(sunset_list),
            }
        )

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

        item.sunrise_average = sunrise_average
        item.sunset_average = sunset_average
        item.detail = detail
        try:
            item.full_clean()
        except Exception as e:
            errors.append('Errors message : %s . [%s %s . Month: %s]' % (str(e), content_type, object, month))
        else:
            item.save()
            self._print('Added %s - Month: %s' % (item.city, item.month))

        if len(errors) == 0:
            self._print('Crawling sucessful %s days' % len(posts))
        else:
            self._print('Errors (%s): ' % len(errors))
            for error in errors:
                self._print('- %s' % error)