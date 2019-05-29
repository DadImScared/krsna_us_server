"""This module contains the class HarmonistMagazineSpider.

It crawls http://www.purebhakti.com/resources/ebooks-a-magazines-mainmenu-63/harmonist-magazine.html
"""
import scrapy

from ..items import HarikathaBotItem


class HarmonistMagazineSpider(scrapy.Spider):
    """Collects all magazine links and saves them with the category harmonistmagazine"""
    name = 'hmagazine'
    start_urls = [
        'http://www.purebhakti.com/resources/ebooks-a-magazines-mainmenu-63/harmonist-magazine.html'
    ]

    def parse(self, response):
        """Collects all links and follows links"""
        for book in response.css('.k-js-grid-controller .docman_document .koowa_header__title_link'):
            yield HarikathaBotItem({
                'link': response.urljoin(book.css('::attr(href)').extract_first().strip()),
                'title': book.css('::text').extract_first().strip(),
                'category': 'harmonistmagazine'
            })

        pages = response.css('form.k-js-grid-controller div.k-pagination li')
        if pages:
            last_item = pages[-1].css("a::text").extract_first()
            # check if last item in pagination list is a next arrow
            try:
                int(last_item)
            except ValueError:
                next_page = response.urljoin(pages[-1].css("a::attr(href)").extract_first())
                yield scrapy.Request(next_page, callback=self.parse)
