"""This module contains the MovieSpider that crawls http://purebhakti.tv/movies.htm"""
import scrapy

from ..items import HarikathaBotItem


class MovieSpider(scrapy.Spider):
    """Collects all movie links and saves them with the category of 'movie'"""
    name = 'movies'
    start_urls = [
        'http://purebhakti.tv/movies.htm'
    ]

    def parse(self, response):
        for item in response.css('div a'):
            yield HarikathaBotItem({
                'link': item.css('::attr(href)').extract_first().strip(),
                'title': item.css('::text').extract_first().strip().replace('\t', '').replace('\n', ''),
                'category': 'movie'
            })
