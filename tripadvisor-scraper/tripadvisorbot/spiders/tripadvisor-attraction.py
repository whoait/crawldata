import re
import time

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request

from tripadvisorbot.items import *
from tripadvisorbot.spiders.crawlerhelper import *


class TripAdvisorAttractionBaseSpider(BaseSpider):
    name = "tripadvisor-attraction"

    allowed_domains = ["tripadvisor.com"]
    base_uri = "http://www.tripadvisor.com"
    start_urls = [
        base_uri + '/Attractions-g298085-Activities-c26-Da_Nang_Quang_Nam_Province.html#TtD',
        base_uri + '/Attractions-g298085-Activities-c42-Da_Nang_Quang_Nam_Province.html#TtD',
        base_uri + '/Attractions-g298085-Activities-c40-Da_Nang_Quang_Nam_Province.html#TtD',
        base_uri + '/Attractions-g298082-Activities-c26-Hoi_An_Quang_Nam_Province.html#TtD',
        base_uri + '/Attractions-g298082-Activities-c42-Hoi_An_Quang_Nam_Province.html#TtD',
        base_uri + '/Attractions-g298082-Activities-c40-Hoi_An_Quang_Nam_Province.html#TtD',
        base_uri + '/Attractions-g293925-Activities-c26-Ho_Chi_Minh_City.html#TtD',
        base_uri + '/Attractions-g293925-Activities-c42-Ho_Chi_Minh_City.html#TtD',
        base_uri + '/Attractions-g293925-Activities-c40-Ho_Chi_Minh_City.html#TtD',
        base_uri + '/Attractions-g293924-Activities-c26-Hanoi.html#TtD',
        base_uri + '/Attractions-g293924-Activities-c42-Hanoi.html#TtD',
        base_uri + '/Attractions-g293924-Activities-c40-Hanoi.html#TtD',
        base_uri + '/Attractions-g469418-Activities-c26-Phu_Quoc_Island_Kien_Giang_Province.html#TtD',
        base_uri + '/Attractions-g469418-Activities-c42-Phu_Quoc_Island_Kien_Giang_Province.html#TtD',
        base_uri + '/Attractions-g469418-Activities-c40-Phu_Quoc_Island_Kien_Giang_Province.html#TtD',
        base_uri + '/Attractions-g293926-Activities-c26-Hue_Thua_Thien_Hue_Province.html#TtD',
        base_uri + '/Attractions-g293926-Activities-c42-Hue_Thua_Thien_Hue_Province.html#TtD',
        base_uri + '/Attractions-g293926-Activities-c40-Hue_Thua_Thien_Hue_Province.html#TtD',
        base_uri + '/Attractions-g1009804-Activities-c26-Mui_Ne_Phan_Thiet_Binh_Thuan_Province.html#TtD',
        base_uri + '/Attractions-g1009804-Activities-c42-Mui_Ne_Phan_Thiet_Binh_Thuan_Province.html#TtD',
        base_uri + '/Attractions-g1009804-Activities-c40-Mui_Ne_Phan_Thiet_Binh_Thuan_Province.html#TtD',
        base_uri + '/Attractions-g293928-Activities-c26-Nha_Trang_Khanh_Hoa_Province.html#TtD',
        base_uri + '/Attractions-g293928-Activities-c42-Nha_Trang_Khanh_Hoa_Province.html#TtD',
        base_uri + '/Attractions-g293928-Activities-c40-Nha_Trang_Khanh_Hoa_Province.html#TtD',
        base_uri + '/Attractions-g311304-Activities-c26-Sapa_Lao_Cai_Province.html#TtD',
        base_uri + '/Attractions-g311304-Activities-c42-Sapa_Lao_Cai_Province.html#TtD',
        base_uri + '/Attractions-g311304-Activities-c40-Sapa_Lao_Cai_Province.html#TtD',
        base_uri + '/Attractions-g293940-Activities-c26-Phnom_Penh.html#TtD',
        base_uri + '/Attractions-g293940-Activities-c42-Phnom_Penh.html#TtD',
        base_uri + '/Attractions-g293940-Activities-c40-Phnom_Penh.html#TtD',
        base_uri + '/Attractions-g608455-Activities-c26-Kampot_Kampot_Province.html#TtD',
        base_uri + '/Attractions-g608455-Activities-c42-Kampot_Kampot_Province.html#TtD',
        base_uri + '/Attractions-g608455-Activities-c40-Kampot_Kampot_Province.html#TtD',
        base_uri + '/Attractions-g608456-Activities-c26-Kep_Kep_Province.html#TtD',
        base_uri + '/Attractions-g608456-Activities-c42-Kep_Kep_Province.html#TtD',
        base_uri + '/Attractions-g608456-Activities-c40-Kep_Kep_Province.html#TtD',
        base_uri + '/Attractions-g297390-Activities-c26-Siem_Reap_Siem_Reap_Province.html#TtD',
        base_uri + '/Attractions-g297390-Activities-c42-Siem_Reap_Siem_Reap_Province.html#TtD',
        base_uri + '/Attractions-g297390-Activities-c40-Siem_Reap_Siem_Reap_Province.html#TtD',
        base_uri + '/Attractions-g325573-Activities-c26-Sihanoukville_Sihanoukville_Province.html#TtD',
        base_uri + '/Attractions-g325573-Activities-c42-Sihanoukville_Sihanoukville_Province.html#TtD',
        base_uri + '/Attractions-g325573-Activities-c40-Sihanoukville_Sihanoukville_Province.html#TtD',
        base_uri + '/Attractions-g295415-Activities-c26-Luang_Prabang_Luang_Prabang_Province.html#TtD',
        base_uri + '/Attractions-g295415-Activities-c42-Luang_Prabang_Luang_Prabang_Province.html#TtD',
        base_uri + '/Attractions-g295415-Activities-c40-Luang_Prabang_Luang_Prabang_Province.html#TtD',
        base_uri + '/Attractions-g293950-Activities-c26-Vientiane_Vientiane_Province.html#TtD',
        base_uri + '/Attractions-g293950-Activities-c42-Vientiane_Vientiane_Province.html#TtD',
        base_uri + '/Attractions-g293950-Activities-c40-Vientiane_Vientiane_Province.html#TtD',
        base_uri + '/Attractions-g612363-Activities-c26-Vang_Vieng_Vientiane_Province.html#TtD',
        base_uri + '/Attractions-g612363-Activities-c42-Vang_Vieng_Vientiane_Province.html#TtD',
        base_uri + '/Attractions-g612363-Activities-c40-Vang_Vieng_Vientiane_Province.html#TtD',
        base_uri + '/Attractions-g670161-Activities-c26-Pakse_Champasak_Province.html#TtD',
        base_uri + '/Attractions-g670161-Activities-c42-Pakse_Champasak_Province.html#TtD',
        base_uri + '/Attractions-g670161-Activities-c40-Pakse_Champasak_Province.html#TtD',
        base_uri + '/Attractions-g1507054-Activities-c26-Ao_Nang_Krabi_Town_Krabi_Province.html#TtD',
        base_uri + '/Attractions-g1507054-Activities-c42-Ao_Nang_Krabi_Town_Krabi_Province.html#TtD',
        base_uri + '/Attractions-g1507054-Activities-c40-Ao_Nang_Krabi_Town_Krabi_Province.html#TtD',
        base_uri + '/Attractions-g293920-Activities-c26-Phuket.html#TtD',
        base_uri + '/Attractions-g293920-Activities-c42-Phuket.html#TtD',
        base_uri + '/Attractions-g293920-Activities-c40-Phuket.html#TtD',
        base_uri + '/Attractions-g293916-Activities-c26-Bangkok.html#TtD',
        base_uri + '/Attractions-g293916-Activities-c42-Bangkok.html#TtD',
        base_uri + '/Attractions-g293916-Activities-c40-Bangkok.html#TtD',
        base_uri + '/Attractions-g293917-Activities-c26-Chiang_Mai.html#TtD',
        base_uri + '/Attractions-g293917-Activities-c42-Chiang_Mai.html#TtD',
        base_uri + '/Attractions-g293917-Activities-c40-Chiang_Mai.html#TtD',
        base_uri + '/Attractions-g293918-Activities-c26-Ko_Samui_Surat_Thani_Province.html#TtD',
        base_uri + '/Attractions-g293918-Activities-c42-Ko_Samui_Surat_Thani_Province.html#TtD',
        base_uri + '/Attractions-g293918-Activities-c40-Ko_Samui_Surat_Thani_Province.html#TtD',
        base_uri + '/Attractions-g293919-Activities-c26-Pattaya_Chonburi_Province.html#TtD',
        base_uri + '/Attractions-g293919-Activities-c42-Pattaya_Chonburi_Province.html#TtD',
        base_uri + '/Attractions-g293919-Activities-c40-Pattaya_Chonburi_Province.html#TtD',
    ]

    def parse(self, response):
        tripadvisor_items = []

        sel = Selector(response)
        snode_restaurants = sel.xpath('//div[@id="FILTERED_LIST"]/div/div[starts-with(@class, "element_wrap")]/div[starts-with(@class, "wrap al_border")]')

        # print snode_restaurants

        # Build item index.
        category_id = re.search(r'[\-c]+[0-9]+[\-]', response.request.url).group(0).replace('-', '')
        
        for snode_restaurant in snode_restaurants:

            tripadvisor_item = TripAdvisorItem()

            tripadvisor_item['url'] = url = self.base_uri + clean_parsed_string(get_parsed_string(snode_restaurant, 'div[starts-with(@class, "entry ")]/div[@class="property_title"]/a/@href'))
            business_id = re.search(r'[\-d]+[0-9]+[\-]', url).group(0).replace('-', '')

            city = re.search(r'[\-]+[A-Z]\w+[/.]', url).group(0).replace('-', '').replace('.', '').replace('_', ' ')
            if city:
                tripadvisor_item['city'] = city

            category = ''
            if category_id:
                if category_id == 'c26':
                    category = 'Shopping & Malls'
                elif category_id == 'c42':
                    category = 'Tours & Activities'
                elif category_id == 'c40':
                    category = 'Spa & Wellness'
            if category:
                tripadvisor_item['category'] = category
                
            tripadvisor_item['business_id'] = business_id
            # print url
            tripadvisor_item['name'] = name = clean_parsed_string(get_parsed_string(snode_restaurant, 'div[starts-with(@class, "entry ")]/div[@class="property_title"]/a/text()'))
            yield Request(url=tripadvisor_item['url'], meta={'tripadvisor_item': tripadvisor_item}, callback=self.parse_search_page)

            tripadvisor_items.append(tripadvisor_item)

        print 'get next page'
        next_page_url = clean_parsed_string(get_parsed_string(sel, '//a[starts-with(@class, "guiArw sprite-pageNext ")]/@href'))

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
            email = re.search(r'[\w\.-]+@[\w\.-]+', email).group(0)

        tripadvisor_item['email'] = email

        # tripadvisor_item['address'] = tripadvisor_address_item

        yield tripadvisor_item