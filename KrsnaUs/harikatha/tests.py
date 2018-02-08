
from django.test import TestCase
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from .models import HarikathaIndex
from .utils import PaginatedQuery
from .factories import UserFactory

# Create your tests here.


class HariKathaCollectionViewTestWithCategories(APITestCase):
    fixtures = ['fulldata.json']

    def test_get_items_with_category_harikatha(self):
        """/items/harikatha should return items under the category harikatha only"""
        response = self.client.get('{}'.format(reverse('items', args=('harikatha',))))
        self.assertEqual(response.status_code, 200)
        for item in response.data:
            self.assertEqual('harikatha', item['category'])


class SearchViewTest(APITestCase):

    def test_search_collection(self):
        """Tests results are returned when a word in the search query matches"""
        response = self.client.get("{}?categories=book&categories=movie&categories=song&page=200".format(
            reverse('search-items', args=('Vraja Mandal Parikram P1',))
        ))
        self.assertTrue(response.status_code)
        self.assertTrue(response.data['results'])

    def test_search_collection_with_typo(self):
        """Tests suggestions are returned when searched with typo"""
        response = self.client.get("{}?categories=book&categories=movie&categories=song&page=200".format(
            reverse('search-items', args=('Vraja Mandl Parikram P1',))
        ))
        self.assertTrue(response.data['suggestions'])
        self.assertTrue(response.data['results'])


class TestPaginatedQuery(TestCase):

    def setUp(self):
        self.query = HarikathaIndex.search().filter('terms', category=['movie'])

    def test_paginated_query(self):
        paged_query = PaginatedQuery(self.query, '/api/v1/search', 'categories=movie', page_number=157)
        self.assertEqual(paged_query.total_items, 3940)
        self.assertEqual(paged_query.total_pages, 158)
        self.assertEqual(paged_query.next_page, '/api/v1/search?categories=movie&page=158')
        self.assertEqual(len(paged_query.query.execute()), 25)


class TestLogin(APITestCase):

    def test_login(self):
        """Tests user can log in and then use token to access protected route"""
        username = 'testuser'
        password = 'testpass'
        User = get_user_model()
        user = User.objects.create_user(username, password=password, email='fakeemail@t.com')
        EmailAddress.objects.create(user=user, email='fakeemail@t.com', primary=True, verified=True)
        response = self.client.post(
            '/rest-auth/login/',
            data={"username": 'testuser', "password": 'testpass', "email": 'fakeemail@t.com'}
        )
        response2 = self.client.get(
            '/api/v1/playlists/',
            {}, HTTP_AUTHORIZATION='Token {}'.format(response.data['key'])
        )
        self.assertEqual(200, response2.status_code)


class TestPlaylists(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_thing(self):
        response = self.client.get(reverse('playlists'))
        print(response.data)
