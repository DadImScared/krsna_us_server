"""This module contains HarmonistMonthlySpider which crawls http://www.purebhakti.com/resources/harmonist-monthly.html
"""
import scrapy

from ..items import HarikathaBotItem


class HarmonistMonthlySpider(scrapy.Spider):
    """Collects all links"""
    name = 'hmonthly'
    start_urls = [
        'http://www.purebhakti.com/resources/harmonist-monthly.html'
    ]

    def parse(self, response):
        """Collects all links with the category harmonistmonthly and follows next page"""
        for item in response.css('.bloghmonthly .items-row'):
            yield HarikathaBotItem({
                'link': response.urljoin(item.css('h2 a::attr(href)').extract_first().strip()),
                'title': item.css('h2 a::text').extract_first().strip(),
                'category': "harmonistmonthly"
            })
        next_page = response.css('.pagination-next a::attr(href)').extract_first()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
