#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'ongzl'

import json
import urllib2
import urllib
from BeautifulSoup import BeautifulSoup


from ..string_util import setuplogger


logger = setuplogger()

level_1_base_url = 'http://www.merriam-webster.com/browse/thesaurus/'
level_2_base_url = 'http://www.merriam-webster.com'

MAX_TRIES = 3

# global storage
# each element has
# eg. ave
# {
#   'word': 'ave',
#   'type': 'noun',
#   'synonymns': ['adieu', 'au revoir', 'ave', 'bon voyage', 'congé', 'farewell', 'Godspeed']
#   'related': ['leave-taking', 'send-off']
#   'near antonymns': ['greeting', 'salutation', 'salute', 'welcome']
#   'antonymn': ['hello']
# }

word_list = []

# function returns soup of a div with browse
# url (str) = start url
# return browse_list (soup)
def find_browse_list(url):
    page_html = None
    retry_counter = 0
    while retry_counter < MAX_TRIES:
        try:
            page_html = urllib2.urlopen(url).read()
            if page_html:
                break
        except urllib2.HTTPError:
            logger.info("HTTPError with url = {0}".format(url))
        retry_counter += 1
    if not page_html:
        logger.info("no page html for url = {0}".format(url))
    soup = BeautifulSoup(page_html)
    body = soup.find("body", id="default-template")
    if not body:
        # ad page - retry with previous URL
        logger.info("we saw an ad with url {0}".format(url))
        return None
    middle_body = body.find("div", id="middle")
    if middle_body:
        if middle_body.find("div", attrs={'class': "entries"}):
            # level_2 - direct entries
            return middle_body.find("div", attrs={'class': "entries"})
        else:
            # level 1 - table of contents
            return middle_body.find("ol", "toc")
    return None


def level_1_list(browse_entries):
    if browse_entries:
        entries_li = list(browse_entries.findAll("li"))
        for entry in entries_li:
            logger.info('level 1 list entry: {0}'.format(entry))
            link = entry.find('a').get('href')
            retry_counter = 0
            if link:
                query_link = level_1_base_url + urllib.quote(link)
                logger.info('query link level 1 = {0}'.format(query_link))
                while retry_counter < MAX_TRIES:
                    browse_soup = find_browse_list(query_link)
                    if browse_soup:
                        level_2_list(browse_soup)
                        break
                    retry_counter += 1


def level_2_list(browse_entries):
    if browse_entries:
        if browse_entries.find('ol'):
            entries_li = list(browse_entries.find('ol').findAll('li'))
            for entry in entries_li:
                link = entry.find('a').get('href')
                query_link = level_2_base_url + urllib.quote(link)
                logger.info('level 2 list entry : {0}, query link = {1}'.format(entry, query_link))
                retry_counter = 0
                while retry_counter < MAX_TRIES:
                    if process_word(query_link):
                        break
                    retry_counter += 1


def process_word(url):
    logger.info("processing word: {0}".format(url))
    retry_counter = 0
    page_html = None
    while retry_counter < MAX_TRIES:
        try:
            page_html = urllib2.urlopen(url).read()
            if page_html:
                break
        except urllib2.HTTPError:
            logger.info("HTTPError with url = {0}".format(url))
        retry_counter += 1
    if not page_html:
        logger.info("we have no page_html for word = {0}".format(url))
        return None
    word_soup = BeautifulSoup(page_html)
    word_dict = {}
    word_entry = word_soup.find('div', id="mwEntryData")
    if word_entry:
        head_word = word_entry.find("div", "headword")
        if head_word:
            word_dict['word'] = head_word.find("h2").text
            word_dict['noun'] = head_word.find("em").text

        scnt_div = word_entry.find('div', 'scnt')
        if scnt_div:
            div_list = list(scnt_div.findAll('div'))
            for div in div_list:
                # find the strong tag to get the first word
                div_property = div.find('strong').text
                div_values = []
                # then find all links
                links = list(div.findAll('a'))
                for link in links:
                    div_values.append(link.text)
                word_dict[div_property] = div_values
    else:
        logger.info("no entry div in process word: {0}".format(url))
        return None

    if word_dict.get('word'):
        # store , otherwise don't store word
        word_list.append(word_dict)
    else:
        logger.info("no word in dict for url = {0} : {1}".format(
            url, word_dict
        ))
        return None
    return True


# start url : http://www.merriam-webster.com/browse/thesaurus/a.htm
start_url = 'http://www.merriam-webster.com/browse/thesaurus/a.htm'
continue_flag = True
try:
    while continue_flag:
        start_soup = BeautifulSoup(
            urllib2.urlopen(start_url).read()
        )

        body = start_soup.find("body", id="default-template")
        if not body:
            # ad page - retry with previous URL
            logger.info("we saw an ad with url {0}".format(start_url))
            continue

        middle_body = body.find("div", id="middle")
        if middle_body:
            if middle_body.find("div", "entries"):
                # level_2 - direct entries
                level_2_list(middle_body.find("div", "entries"))
            else:
                # level 1 - table of contents
                level_1_list(middle_body.find("ol", "toc"))

        pagination_soup = body.find("div", "pagination")
        if pagination_soup.find("a", "button next"):
            start_url = level_1_base_url + pagination_soup.find("a", "button next").get('href')
        else:
            continue_flag = False
            logger.info("reached end of crawl at start url = {0}".format(start_url))

except:
    logger.error('error in main loop')
finally:
    with open("crawl_dict.json", 'w') as fp:
        json.dump(word_list, fp, indent=4, separators=(",", ": "))
