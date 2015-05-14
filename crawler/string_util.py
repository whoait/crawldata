"""
Base item class
"""
import string
import pymongo
import math
import logging
import time
from time import mktime
from datetime import datetime
import re, urllib2, urlparse
from selenium import webdriver
from BeautifulSoup import BeautifulSoup
import uuid


html_escape_table = {
    "&amp;":"&",
    "&quot;":'"',
    "&apos;":"'",
    "&gt;":">",
    "&lt;":"<",
    "&#39;" : "'",
    "&#x201c;":'"',
    "&#x201d;":'"',
    }

def html_escape(text):
    """Produce entities within text."""
    return reduce(lambda x, y: x.replace(y, html_escape_table[y]),
            html_escape_table, text)
    # return "".join(html_escape_table.get(c,c) for c in text)


def common_start(sa, sb):
    """ returns the longest common substring from the beginning of sa and sb """
    def _iter():
        for a, b in zip(sa, sb):
            if a == b:
                yield a
            else:
                return

    return ''.join(_iter())

def tokenize(string):
    """Tokenizes a string, returning a list (of strings).
    Algorithm:
    (1) split the string along whitespace, numeric, and selected punctuation;
    (2) squash all subsequent non-alphanumeric.
    """
    R1 = re.compile(r'[\d\s-]+')
    R2 = re.compile(r'\W+')
    tokens = []
    for s1 in re.split(R1, string) :
        s2 = re.sub(R2, '', s1)
        if s2 == '' :
            continue
        tokens.append(s2.lower())
    return tokens

def setuplogger(loggername='crawler', loglevel=logging.INFO):
    logger = logging.getLogger(loggername)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)
    return logger


def filter_description(input_string):
    # 1. remove HTML tags and replace with spaces
    p = re.compile('<.*?>')
    intermediate_string = p.sub(' ', input_string).\
                            replace('\r', '').\
                            replace('\n', '').strip()

    # 2. remove newline characters
    return re.sub('\s[.,]', strip_punctuation_whitespace, intermediate_string)


def strip_punctuation_whitespace(matchobj):
    return matchobj.group(0).split(' ')[1]