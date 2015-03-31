# from scrapy.spider import Spider
# from scrapy import Selector
# from thebesttimetovisit.items import TheBestTimeToVisitItem
# from main.models import City, CityWeatherMonth
#
# def month_to_num(month):
#
#     return{
#             'january'   : 1,
#             'february'  : 2,
#             'march'     : 3,
#             'april'     : 4,
#             'may'       : 5,
#             'june'      : 6,
#             'july'      : 7,
#             'august'    : 8,
#             'september' : 9,
#             'october'   : 10,
#             'november'  : 11,
#             'december'  : 12
#     }[month]
#
#
# # run this command : python manage.py scrapy crawl thebesttimetovisit
# class TheBestTimeToVisitSpider(Spider):
#     name = "thebesttimetovisit"
#     allowed_domains = ["thebesttimetovisit.com"]
#     start_urls = [
#         "http://www.thebesttimetovisit.com/weather/bangkok-idvilleeng-93.html"
#     ]
#
#     counter = 0
#     max_page = 100000
#
#     def parse(self, response):
#         self.counter += 1
#
#         base_url = "http://www.thebesttimetovisit.com"
#         hxs = Selector(response)
#
#         posts = hxs.xpath('//table[@cellpadding="2"]/tr')
#
#         if posts:
#             del posts[0]
#
#         # TODO: find a way to know which city that we're crawling data, now 293916 is Bangkok in main_city
#         city = City.objects.get(id=293916)
#         for post in posts:
#             rows = post.xpath('td/text()').extract()
#             item = TheBestTimeToVisitItem()
#             item['city'] = city
#             item['month'] = month_to_num(rows[0])
#             item['sunlight'] = rows[1]
#             item['average_min'] = rows[2]
#             item['average_max'] = rows[3]
#             item['record_min'] = rows[4]
#             item['record_max'] = rows[5]
#             item['precipitations'] = rows[6]
#             item['wet_days'] = rows[7]
#             item.save()