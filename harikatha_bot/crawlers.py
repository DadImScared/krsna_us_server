"""This module runs all the spiders programmatically"""


from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl('hmagazine')
    process.crawl('books')
    process.crawl('bhagavatpatrika')
    process.crawl('hmonthly')
    process.crawl('songs')
    process.crawl('movies')
    process.crawl('lectures')
    process.crawl('hknewsletter')
    process.crawl('hk1996')
    process.start()
