"""This module contains the class BookSpider.

It crawls http://www.purebhakti.com/resources/ebooks-a-magazines-mainmenu-63/bhakti-books/
"""
import scrapy

from ..items import HarikathaBotItem


class BookSpider(scrapy.Spider):
    """Collects all books from the start_urls attr and saves with category 'book'"""
    name = 'books'
    start_urls = [
        'http://www.purebhakti.com/resources/ebooks-magazines/bhakti-books/english',
        'http://www.purebhakti.com/resources/ebooks-magazines/bhakti-books/bengali',
        'http://www.purebhakti.com/resources/ebooks-magazines/bhakti-books/german',
        'http://www.purebhakti.com/resources/ebooks-magazines/bhakti-books/hindi',
        'http://www.purebhakti.com/resources/ebooks-magazines/bhakti-books/russian',
        'http://www.purebhakti.com/resources/ebooks-magazines/bhakti-books/spanish'
    ]

    def parse(self, response):
        """Collects all book links and follows next page"""
        for book in response.css('form.k-js-grid-controller .docman_document .koowa_header__title_link'):

            language = response.url.rsplit("/", 1)[1].split("?")[0]

            yield HarikathaBotItem({
                'link': response.urljoin(book.css('::attr(href)').extract_first().strip()),
                'title': book.css('::text').extract_first().strip(),
                'language': language,
                'category': 'book'
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
