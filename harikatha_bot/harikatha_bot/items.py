# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem

# this works even though pycharm is saying it doesn't
from harikatha.models import HarikathaCollection


class HarikathaBotItem(DjangoItem):
    """Item to save scraped data to HarikathaCollect database table"""
    django_model = HarikathaCollection
