
import math
from furl import furl


def next_page(query_string, page_number, last_page, search_query):
    """Return url to next page if it exists else false"""
    if last_page:
        return False
    f = furl('/api/v1/search/{}'.format(search_query))
    f.set(query=query_string)
    f.args.pop('page', '')
    f.args.add('page', page_number + 1)
    return f.url


def get_page_number(page_number, page_size, total_items):
    """Check if page_number is in bounds of total pages

    :param int page_number: Page number
    :param int page_size: Items per page
    :param int total_items: Total item count
    :return: Tuple of page_number or a page in bounds of total pages and page_number is last page
    """
    try:
        int(page_number)
    except ValueError:
        return get_page_number(1, page_size, total_items)
    else:
        page_number = int(page_number)
        total_pages = int(math.ceil(float(total_items)/page_size))
        if total_items == 0:
            return 1, True
        if page_number < 1:
            new_number = 1
        elif page_number > total_pages:
            new_number = total_pages
        else:
            new_number = page_number
        return new_number, new_number == total_pages


def paginate_query(elastic_query, page_size, page_number):
    """Paginate the elastic search query"""
    offset = (page_number - 1) * page_size
    return elastic_query[offset:offset + page_size]


class PaginatedQuery:
    def __init__(self, elastic_query, relative_path, query_string, page_number=1, page_size=25):
        self.original_query = elastic_query
        self.total_items = self.original_query.count()
        self.path = relative_path
        self._query_string = query_string
        self._page_number = page_number
        self.page_size = page_size
        self.total_pages = int(math.ceil(float(self.total_items)/self.page_size))
        self.page_number = self.get_page_number(page_number)
        self.last_page = self.page_number == self.total_pages or self.total_items == 0
        self.next_page = self.get_next_page()
        self.offset = (self.page_number - 1) * page_size
        self.query = self.original_query[self.offset:self.offset + page_size]

    @property
    def query_string(self):
        return self._query_string

    @query_string.setter
    def query_string(self, value):
        self._query_string = value

    def get_page_number(self, page_num):
        try:
            page_number = int(page_num)
        except ValueError:
            return self.get_page_number(1)
        else:
            if self.total_items == 0:
                return 1
            if page_number < 1:
                return 1
            elif page_number > self.total_pages:
                return self.total_pages
            else:
                return page_number

    def get_next_page(self):
        if self.last_page:
            return False
        frl = furl('{}?{}'.format(self.path, self.query_string))
        frl.args.pop('page', '')
        frl.args.add('page', self.page_number + 1)
        return frl.url
