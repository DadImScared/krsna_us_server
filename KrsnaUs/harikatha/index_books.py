
import django
import os
import re
import sys
from elasticsearch_dsl.connections import connections
sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KrsnaUs.settings")
django.setup()

from harikatha import models, search

dir_path = os.path.dirname(os.path.realpath(__file__))
book_dir = '{0}{1}allbooks{1}'.format(dir_path, os.path.sep)
files = os.listdir(book_dir)


def get_book(path):
    try:
        with open('{}{}'.format(book_dir, path), "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(path)
        print("path not found")
        return False

page_split = r'[\s]{26}[0-9]{1,4}[^0-9/.-_\\|()\[\]]'


def index_book_content():
    # get all english books that haven't been indexed
    books = models.HarikathaCollection.objects.filter(
        category='book',
        language__in=['english', 'hindi'],
        indexed=False
    )
    for book in books:
        book_file = get_book('{}.txt'.format(book.title))
        if book_file:
            pages = re.split(page_split, book_file)
            for i, page in enumerate(pages):
                search.HarikathaIndex(
                    content_title=book.title,
                    link=book.link,
                    language=book.language,
                    page=i+1,
                    body=page,
                    body_suggest=page,
                    category='book',
                    item_id=book.item_id
                ).save()
            book.indexed = True
            book.save()

if __name__ == '__main__':
    index_book_content()
