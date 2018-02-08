"""This module contains the class BookSpider.

It crawls http://www.purebhakti.com/resources/ebooks-a-magazines-mainmenu-63/bhakti-books/
"""
import scrapy

from ..items import HarikathaBotItem


class BookSpider(scrapy.Spider):
    """Collects all books from the start_urls attr and saves with category 'book'"""
    name = 'books'
    start_urls = [
        'http://www.purebhakti.com/resources/ebooks-a-magazines-mainmenu-63/bhakti-books/english.html',
        'http://www.purebhakti.com/resources/ebooks-a-magazines-mainmenu-63/bhakti-books/bengali.html',
        'http://www.purebhakti.com/resources/ebooks-a-magazines-mainmenu-63/bhakti-books/german.html',
        'http://www.purebhakti.com/resources/ebooks-a-magazines-mainmenu-63/bhakti-books/hindi.html',
        'http://www.purebhakti.com/resources/ebooks-a-magazines-mainmenu-63/bhakti-books/russian.html',
        'http://www.purebhakti.com/resources/ebooks-a-magazines-mainmenu-63/bhakti-books/spanish.html'
    ]

    def parse(self, response):
        """Collects all book links and follows next page"""
        for book in response.css('.-koowa-grid .docman_document'):

            language = response.url.rsplit('.', 1)[0].rsplit('/', 1)[1]
            yield HarikathaBotItem({
                'link': response.urljoin(book.css('.docman_download__button::attr(href)').extract_first().strip()),
                'title': book.css('.koowa_header__title_link span::text').extract_first().strip(),
                'language': language,
                'category': 'book'
            })

        pages = response.css('.pagination-list li')
        if pages:
            last_item = pages[-1].css("a::text").extract_first()
            # check if last item in pagination list is a next arrow
            try:
                int(last_item)
            except ValueError:
                next_page = response.urljoin(pages[-1].css("a::attr(href)").extract_first())
                yield scrapy.Request(next_page, callback=self.parse)
