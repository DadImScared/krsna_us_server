"""This module contains the class SongSpider that crawls http://sbnmcd.org/extradisk/bhajan/"""
import scrapy

from ..items import HarikathaBotItem

mp3_list = ['mp3', 'wav']


class SongSpider(scrapy.Spider):
    """This spider collects all audio files and parses top level directories and saves files as category 'song'"""
    name = 'songs'
    start_urls = ['http://sbnmcd.org/extradisk/bhajan/']

    def parse(self, response):
        """Collects all directories and top level audio files"""
        for directory in response.css('.folder_bg a'):
            yield scrapy.Request(
                response.urljoin(directory.css("::attr(href)").extract_first()),
                callback=self.parse_directory,
                meta={'category': directory.css("::text").extract_first()}
            )

        for item in response.css('tr a'):
            if item.css("::attr(href)").extract_first()[-3:].lower() in mp3_list:
                yield HarikathaBotItem(**{
                    'link': response.urljoin(item.css("::attr(href)").extract_first()),
                    'title': item.css("::text").extract_first(),
                    'directory': 'general',
                    'category': 'song'
                })

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
