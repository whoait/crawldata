import re
import time

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request

from tripadvisorbot.items import *
from tripadvisorbot.spiders.crawlerhelper import *


class TripAdvisorRestaurantBaseSpider(BaseSpider):
    name = "tripadvisor-restaurant"

    allowed_domains = ["tripadvisor.com"]
    base_uri = "http://www.tripadvisor.com"
    start_urls = [
        base_uri + '/Restaurants-g469418-Phu_Quoc_Island_Kien_Giang_Province.html',
        base_uri + '/Restaurants-g293920-Phuket.html',
    ]

    def parse(self, response):
        tripadvisor_items = []

        sel = Selector(response)
        snode_restaurants = sel.xpath('//div[@id="EATERY_SEARCH_RESULTS"]/div[starts-with(@class, "listing")]')

        # Build item index.
        for snode_restaurant in snode_restaurants:

            tripadvisor_item = TripAdvisorItem()

            tripadvisor_item['url'] = url = self.base_uri + clean_parsed_string(get_parsed_string(snode_restaurant, 'div[starts-with(@class, "shortSellDetails")]/h3[@class="title"]/a[@class="property_title"]/@href'))
            business_id = re.search(r'[\-d]+[0-9]+[\-]', url).group(0).replace('-', '')
            
            city = re.search(r'[\-]+[A-Z]\w+[/.]', url).group(0).replace('-', '').replace('.', '').replace('_', ' ')
            if city:
                tripadvisor_item['city'] = city

            category = 'Restaurant'
            tripadvisor_item['category'] = category
        
            tripadvisor_item['business_id'] = business_id
            # print url
            tripadvisor_item['name'] = name = clean_parsed_string(get_parsed_string(snode_restaurant, 'div[starts-with(@class, "shortSellDetails")]/h3[@class="title"]/a[@class="property_title"]/text()'))
            yield Request(url=tripadvisor_item['url'], meta={'tripadvisor_item': tripadvisor_item}, callback=self.parse_search_page)

            tripadvisor_items.append(tripadvisor_item)

        print 'get next page'
        next_page_url = clean_parsed_string(get_parsed_string(sel, '//a[starts-with(@class, "nav next rndBtn rndBtnGreen ")]/@href'))

        print next_page_url

        if next_page_url and len(next_page_url) > 0:
            yield Request(url=self.base_uri + next_page_url, callback=self.parse)

    def parse_search_page(self, response):
        tripadvisor_item = response.meta['tripadvisor_item']
        sel = Selector(response)


        # TripAdvisor address for item.
        snode_address = sel.xpath('//div[@class="info_wrapper"]')
        # tripadvisor_address_item = TripAdvisorAddressItem()

        tripadvisor_item['street'] = clean_parsed_string(get_parsed_string(snode_address, 'address/span/span[@class="format_address"]/span[@class="street-address"]/text()'))

        snode_address_postal_code = clean_parsed_string(get_parsed_string(snode_address, 'address/span/span[@class="format_address"]/span[@class="locality"]/span[@property="v:postal-code"]/text()'))
        if snode_address_postal_code:
            tripadvisor_item['postal_code'] = snode_address_postal_code

        snode_address_locality = clean_parsed_string(get_parsed_string(snode_address, 'address/span/span[@class="format_address"]/span[@class="locality"]/span[@property="v:locality"]/text()'))
        if snode_address_locality:
            tripadvisor_address_item['locality'] = snode_address_locality

        tripadvisor_item['country'] = clean_parsed_string(get_parsed_string(snode_address, 'address/span/span[@class="format_address"]/span[@class="locality"]/span[@property="v:region"]/text()'))

        tripadvisor_item['phone'] = clean_parsed_string(get_parsed_string(snode_address, 'div[@class="contact_info"]/div[@class="odcHotel blDetails"]/div[@class="fl notLast"]/div[@class="fl phoneNumber"]/text()'))

        email = clean_parsed_string(get_parsed_string(snode_address, 'div[@class="contact_info"]/div[@class="odcHotel blDetails"]/div[@class="fl notLast"]/div[@class="taLnk hvrIE6 fl"]/@onclick'))

        if email:
            print 'hehehe %s' % email
            email = re.search(r'[\w\.-]+@[\w\.-]+', email).group(0)

        tripadvisor_item['email'] = email

        # tripadvisor_item['address'] = tripadvisor_address_item

        yield tripadvisor_item