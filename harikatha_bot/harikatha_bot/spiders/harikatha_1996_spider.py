
import scrapy

from ..items import HarikathaBotItem


def format_title(title: str) -> str:
    if '1996' in title:
        return title
    elif title.startswith('96'):
        return '19' + title
    else:
        return '1996' + title


class Harikatha96Spider(scrapy.Spider):
    name = 'hk1996'
    start_urls = [
        'http://purebhakti.tv/96/'
    ]

    def parse(self, response):
        # ignore first link since it's a parent directory link
        for item in response.css('tr td a')[1:]:
            yield HarikathaBotItem({
                'link': response.urljoin(item.css('::attr(href)').extract_first().strip()),
                'title': format_title(item.css('::text').extract_first().strip().replace('.html', '')),
                'category': 'harikatha'
            })
