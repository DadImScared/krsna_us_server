"""This module contains the class HariKathaSpider it crawls http://www.purebhakti.com/"""
import scrapy

from ..items import HarikathaBotItem

class HariKathaSpider(scrapy.Spider):
    """Collects all links in the content section on the homepage and saves them with the category harikatha"""
    name = "hknewsletter"

    def start_requests(self):
        urls = [
            'http://www.purebhakti.com/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Collects all links and follows next page"""
        for quote in response.css('.blog-featuredhas-side .items-row .item h2'):
            yield HarikathaBotItem({
                'link': response.urljoin(quote.css('a::attr(href)').extract_first().strip()),
                'title': quote.css('a::text').extract_first().strip(),
                'category': 'harikatha'
            })

        next_page = response.css('.blog-featuredhas-side .pagination-next a::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
