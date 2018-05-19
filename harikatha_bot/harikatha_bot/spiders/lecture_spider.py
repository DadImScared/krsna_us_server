"""This module contains the class AudioLectureSpider that crawls 'http://sbnmcd.org/All_mp3/'"""
import scrapy
import re
import urllib.request

from ..items import HarikathaBotItem


class AudioLectureSpider(scrapy.Spider):
    """This spider collects all mp3 files and follows all directories and collects mp3 files in the directory"""
    name = 'lectures'
    start_urls = ['https://sbnmcd.org/All_mp3/']

    def parse(self, response):
        """Collects all directories and audio files"""
        for item in response.css('td a'):
            if '.' not in item.css('::attr(href)').extract_first():
                directory = item.css("::attr(href)").extract_first()
                yield scrapy.Request(response.urljoin(directory), callback=self.parse_directories)
            elif '.mp3' in item.css('::attr(href)').extract_first():
                yield HarikathaBotItem(**{
                    'link': response.urljoin(item.css("::attr(href)").extract_first()),
                    'title': item.css('::text').extract_first(),
                    'directory': 'general',
                    'category': 'lecture'
                })

    def parse_directories(self, response):
        """Collects all audio files in directory"""
        mp3_list = ['mp3', 'wav']
        category = response.url.rsplit('/', 1)[0].rsplit('/', 1)[1]
        if re.match(r'^[0-9]{4}-?[0-9]{0,4}$', category):
            category = 'general'
        category = urllib.request.unquote(category)
        category = re.sub(r'^[0-9]{1,}', '', category)
        for item in response.css('a'):
            if item.css('::attr(href)').extract_first()[-3:].lower() in mp3_list:
                yield HarikathaBotItem(**{
                    'link': response.urljoin(item.css("::attr(href)").extract_first()),
                    'title': item.css("::text").extract_first(),
                    'directory': category.strip(),
                    'category': 'lecture'
                })
