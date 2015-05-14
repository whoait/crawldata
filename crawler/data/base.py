"""
Base Review class
"""
import string
import pymongo
import math
import logging
from ..string_util import setuplogger 

class Baseclass(object):

    def __init__(self):
        self.logger = setuplogger(loggername=__name__)

    def parse(self, parser):
        raise NotImplementedError()

    def write(self, mongodb):
        raise NotImplementedError()

    def __repr__(self):
        return "Baseclass dummy print"

