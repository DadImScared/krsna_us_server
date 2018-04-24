
import django
import os
import sys
from bs4 import BeautifulSoup as bs
from urllib.request import Request, urlopen
sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KrsnaUs.settings")
django.setup()

from harikatha import models, search


def index_harikatha():
    magazines = models.HarikathaCollection.objects.filter(category='harikatha', indexed=False)
    for magazine in magazines:
        url = magazine.link
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            soup = bs(urlopen(req), 'html.parser')
        except UnicodeEncodeError:
            continue
        article = soup.find('div', class_='item-pagelectures')
        if article:
            content = article.find_all('p')
            body = " ".join([p.get_text() for p in content])
            search.HarikathaIndex(
                content_title=magazine.title,
                body=body,
                body_suggest=body,
                link=url,
                category='harikatha',
                item_id=magazine.item_id,
            ).save()
            magazine.indexed = True
            magazine.save()


def index_harmonist_magazine():
    magazines = models.HarikathaCollection.objects.filter(category='harmonistmonthly', indexed=False)
    for magazine in magazines:
        url = magazine.link
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            soup = bs(urlopen(req), 'html.parser')
        except UnicodeEncodeError:
            continue
        article = soup.find('div', class_='item-pagehmonthly')
        content = article.find_all('p')
        body = " ".join([p.get_text() for p in content])
        search.HarikathaIndex(
            content_title=magazine.title,
            body=body,
            body_suggest=body,
            link=url,
            category='harmonistmonthly',
            item_id=magazine.item_id,
        ).save()
        magazine.indexed = True
        magazine.save()


if __name__ == '__main__':
    index_harikatha()
    index_harmonist_magazine()
