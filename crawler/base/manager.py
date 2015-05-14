"""
Base manager to manage crawling flow
"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from .crawler import BaseCrawler
from .parse_hotel import BaseHotel
from .parse_review import BaseReview


class BaseManager(object):
    def __init__(self):
        pass

    def crawl(self, url=None, filepath=None):
        raise NotImplementedError()

if __name__ == "__main__":
    manager = BaseManager()

    # main()
