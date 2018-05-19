"""This module contains the class SongSpider that crawls http://sbnmcd.org/extradisk/bhajan/"""
import scrapy

from ..items import HarikathaBotItem

mp3_list = ['mp3', 'wav']


class SongSpider(scrapy.Spider):
    """This spider collects all audio files and parses top level directories and saves files as category 'song'"""
    name = 'songs'
    start_urls = ['https://sbnmcd.org/extradisk/bhajan/']

    custom_settings = {
        'ITEM_PIPELINES': {
            'harikatha_bot.pipelines.SongPipeline': 300,
            'harikatha_bot.pipelines.HarikathaBotPipeline': 400
        }
    }

    def parse(self, response):
        """Collects all directories and top level audio files"""
        # for directory in response.css('.folder_bg a'):
        #     print(response.css('.folder_bg a'))
        #     yield scrapy.Request(
        #         response.urljoin(directory.css("::attr(href)").extract_first()),
        #         callback=self.parse_directory,
        #         meta={'category': directory.css("::text").extract_first()}
        #     )

        for item in response.css('tr')[3:]:
            if item.css('a::attr(href)').extract_first().lower().endswith('.mp3'):
                yield HarikathaBotItem(**{
                    'link': response.urljoin(item.css("a::attr(href)").extract_first()),
                    'title': item.css("a::text").extract_first(),
                    'directory': 'general',
                    'category': 'song'
                })
            else:
                yield scrapy.Request(
                    response.urljoin(item.css("a::attr(href)").extract_first()),
                    callback=self.parse_directory,
                    meta={'category': item.css("a::text").extract_first().strip('/')}
                )

        # for item in response.css('tr a'):
        #     if item.css("::attr(href)").extract_first()[-3:].lower() in mp3_list:
        #         yield HarikathaBotItem(**{
        #             'link': response.urljoin(item.css("::attr(href)").extract_first()),
        #             'title': item.css("::text").extract_first(),
        #             'directory': 'general',
        #             'category': 'song'
        #         })

    def parse_directory(self, response):
        """Collects all audio files in directory"""
        category = response.meta['category']

        for item in response.css('tr a'):
            if item.css("::attr(href)").extract_first()[-3:].lower() in mp3_list:
                yield HarikathaBotItem(**{
                    'link': response.urljoin(item.css("::attr(href)").extract_first()),
                    'title': item.css("::text").extract_first(),
                    'directory': category,
                    'category': 'song'
                })
