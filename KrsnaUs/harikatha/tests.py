
import inspect
from django.contrib.auth.models import Permission
from django.utils.http import urlencode
from django.test import TestCase
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from .admin import HariKathaCollectionForm
from .models import HarikathaIndex, Playlists
from .utils import PaginatedQuery
from . import factories

# Create your tests here.


def url_with_query_string(path, query_params):
    """Helper function to combine reverse(path_name) and query string params

    :param path: path from drf reverse
    :param dict query_params: dict for query string example: {'playlist_id': '1222324'}
    :return: Formatted string of path and query_params
    """
    return '{}?{}'.format(path, urlencode(query_params))


def clean_up_factories():
    """Helper function to reset_sequences on functions."""
    for name, obj in inspect.getmembers(factories):
        if inspect.isclass(obj) and "factory" in name.lower():
            obj.reset_sequence(0)


class BaseTestCase(APITestCase):

    def setUp(self):
        self.user = factories.UserFactory(playlists=5, playlists__items=10)
        self.playlist = self.user.playlists.all()[0]
        self.items = self.playlist.items.all()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        clean_up_factories()


class HariKathaCollectionViewTestWithCategories(APITestCase):
    fixtures = ['fulldata.json']

    def test_get_items_with_category_harikatha(self):
        """/items/harikatha should return items under the category harikatha only"""
        response = self.client.get('{}'.format(reverse('items', args=('harikatha',))))
        self.assertEqual(response.status_code, 200)
        for item in response.data:
            self.assertEqual(item['category'], 'harikatha')


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
            data={"password": 'testpass', "email": 'fakeemail@t.com'}
        )
        response2 = self.client.get(
            '/api/v1/playlists/',
            {}, HTTP_AUTHORIZATION='Token {}'.format(response.data['key'])
        )
        self.assertEqual(200, response2.status_code)


class TestPlaylists(BaseTestCase):
    def test_user_can_create_playlist(self):
        before_count = Playlists.objects.count()
        playlist_name = 'my playlist'
        response = self.client.post(reverse('playlists-list'), {"name": playlist_name})
        after_count = Playlists.objects.count()
        self.assertNotEqual(before_count, after_count)
        self.assertEqual(response.data['name'], playlist_name)
        self.assertEqual(
            Playlists.objects.get(playlist_id=response.data['playlist_id']).creator.username,
            self.user.username
        )

    def test_user_can_update_playlist(self):
        new_name = 'new name'
        response = self.client.patch(
            reverse('playlists-detail', args=(self.playlist.playlist_id,)),
            {"name": new_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], new_name)
        self.assertEqual(response.data['playlist_id'], str(self.playlist.playlist_id))

    def test_user_can_retrieve_playlist(self):
        response = self.client.get(reverse('playlists-detail', args=(self.playlist.playlist_id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['playlist_id'], str(self.playlist.playlist_id))
        self.assertEqual(response.data['name'], self.playlist.name)

    def test_user_can_view_all_playlists(self):
        all_playlists = Playlists.objects.all()
        response = self.client.get(reverse('playlists-all-playlists'))
        self.assertEqual(all_playlists.count(), response.data['count'])
        self.assertEqual(response.data['results'][0]['playlist_id'], str(all_playlists[0].playlist_id))

    def test_un_authenticated_user_can_view_all_playlists(self):
        self.client.logout()
        all_playlists = Playlists.objects.all()
        response = self.client.get(reverse('playlists-all-playlists'))
        self.assertEqual(all_playlists.count(), response.data['count'])
        self.assertEqual(response.data['results'][0]['playlist_id'], str(all_playlists[0].playlist_id))

    def test_un_authenticated_user_can_view_playlist_detail(self):
        self.client.logout()
        response = self.client.get(reverse('playlists-detail', args=(self.playlist.playlist_id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['playlist_id'], str(self.playlist.playlist_id))

    def test_has_item_endpoint(self):
        """has_item_endpoint should return playlist with field hasItem equal to item_id or False"""
        item = factories.HarikathaCollectionFactory()
        second_playlist = self.user.playlists.all()[1]
        self.playlist.items.add(
            factories.PlaylistItemFactory.create(collection_item=item, playlist=self.playlist)
        )
        second_playlist.items.add(
            factories.PlaylistItemFactory.create(collection_item=item, playlist=second_playlist)
        )
        response = self.client.get(
            url_with_query_string(reverse('playlists-has-item'), {"item_id": item.item_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)
        self.assertEqual(response.data[0]['hasItem'], self.playlist.items.last().item_id)
        self.assertTrue(response.data[0]['hasItem'])
        self.assertTrue(response.data[1]['hasItem'])
        self.assertEqual(response.data[1]['hasItem'], second_playlist.items.last().item_id)
        for playlist in response.data[2:]:
            self.assertFalse(playlist['hasItem'])


class TestPlaylistItems(BaseTestCase):
    def test_user_can_retrieve_playlist_items(self):
        response = self.client.get(url_with_query_string(
            reverse('items-list'), {'playlist_id': self.playlist.playlist_id}
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.playlist.name)
        self.assertEqual(response.data['items_count'], self.playlist.items.count())
        self.assertTrue(response.data['isCreator'])

    def test_un_authenticated_user_can_retrieve_playlist_items(self):
        self.client.logout()
        response = self.client.get(url_with_query_string(
            reverse('items-list'), {'playlist_id': self.playlist.playlist_id}
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.playlist.name)
        self.assertEqual(response.data['items_count'], self.playlist.items.count())
        self.assertFalse(response.data['isCreator'])

    def test_isCreator_is_false_when_user_is_not_creator(self):
        self.client.logout()
        other_user = factories.UserFactory()
        self.client.force_authenticate(user=other_user)
        response = self.client.get(url_with_query_string(
            reverse('items-list'), {'playlist_id': self.playlist.playlist_id}
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.playlist.name)
        self.assertEqual(response.data['items_count'], self.playlist.items.count())
        self.assertFalse(response.data['isCreator'])

    def test_user_can_retrieve_playlist_item(self):
        item_id = self.items[0].item_id
        response = self.client.get(reverse('items-detail', args=(item_id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_id'], str(item_id))
        self.assertEqual(response.data['title'], self.items[0].collection_item.title)
        self.assertEqual(response.data['link'], self.items[0].collection_item.link)
        self.assertEqual(response.data['category'], self.items[0].collection_item.category)

    def test_user_can_create_playlist_item(self):
        playlist = self.user.playlists.all()[0]
        item_count = self.playlist.items.count()
        collection_item = factories.HarikathaCollectionFactory()
        response = self.client.post(
            url_with_query_string(reverse('items-list'), {'playlist_id': playlist.playlist_id}),
            {"collection_item": collection_item.item_id}
        )
        new_item_count = self.playlist.items.count()
        self.assertNotEqual(item_count, new_item_count)
        self.assertEqual(response.data['item_order'], playlist.items.count() - 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['item_id'], str(playlist.items.last().item_id))
        self.assertEqual(response.data['title'], collection_item.title)
        self.assertEqual(response.data['link'], collection_item.link)
        self.assertEqual(response.data['category'], collection_item.category)

    def test_user_can_delete_playlist_item(self):
        item = self.items.all()[2]
        response = self.client.delete(reverse('items-detail', args=(item.item_id,)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            [playlist_item.item_order for playlist_item in self.playlist.items.all()],
            [_ for _ in range(self.playlist.items.count())]
        )

    def test_user_can_not_create_duplicate_playlist_item(self):
        playlist = self.user.playlists.all()[0]
        collection_item = factories.HarikathaCollectionFactory()
        response = self.client.post(
            url_with_query_string(reverse('items-list'), {'playlist_id': playlist.playlist_id}),
            {"collection_item": collection_item.item_id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response2 = self.client.post(
            url_with_query_string(reverse('items-list'), {'playlist_id': playlist.playlist_id}),
            {"collection_item": collection_item.item_id}
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_move_playlist_item_up_playlist(self):
        playlist = self.user.playlists.all()[0]
        item = playlist.items.last()
        response = self.client.patch(
            reverse('items-detail', args=(item.item_id,)),
            {"new_order": 0}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_order'], 0)
        self.assertNotEqual(item, playlist.items.last())
        self.assertEqual(item, playlist.items.first())

        # asserts all items in the playlist have an order to match the total amount of items
        self.assertEqual([playlist_item.item_order for playlist_item in playlist.items.all()], [_ for _ in range(10)])

    def test_user_can_move_playlist_item_down_playlist(self):
        item = self.items.first()
        new_order = 8
        response = self.client.patch(
            url_with_query_string(
                reverse('items-detail', args=(item.item_id,)), {'playlist_id': self.playlist.playlist_id}
            ),
            {"new_order": new_order}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_order'], new_order)
        self.assertEqual(
            [playlist_item.item_order for playlist_item in self.playlist.items.all()], [_ for _ in range(10)]
        )

    def test_user_can_not_move_playlist_item_down_out_of_range(self):
        """Tests user can not move playlist item out of range.

        The intended result is the item is moved to the last item order.
        """
        item = self.playlist.items.first()
        new_order = 100
        response = self.client.patch(
            url_with_query_string(
                reverse('items-detail', args=(item.item_id,)), {'playlist_id': self.playlist.playlist_id}
            ),
            {"new_order": new_order}
        )
        self.assertEqual(response.data['item_order'], self.playlist.items.count() - 1)
        self.assertEqual(
            [playlist_item.item_order for playlist_item in self.playlist.items.all()], [_ for _ in range(10)]
        )

    def test_user_can_not_move_playlist_item_below_0(self):
        """Tests user can not move playlist item below 0.

        The intended result is the item is moved to the first position 0.
        """
        item = self.items.last()
        new_order = -25
        response = self.client.patch(
            url_with_query_string(
                reverse('items-detail', args=(item.item_id,)), {'playlist_id': self.playlist.playlist_id}
            ),
            {"new_order": new_order}
        )
        self.assertEqual(response.data['item_order'], 0)
        self.assertEqual(9, self.playlist.items.last().item_order)
        self.assertEqual(
            [playlist_item.item_order for playlist_item in self.playlist.items.all()], [_ for _ in range(10)]
        )


class TestUserCantWriteOrDeleteOthersPlaylistOrItems(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.other_user = factories.UserFactory()
        self.other_playlist = self.other_user.playlists.first()

    def assertForbidden(self, response):
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_can_not_delete_playlist(self):
        response = self.client.delete(reverse('playlists-detail', args=(self.other_playlist.playlist_id,)))
        self.assertForbidden(response)

    def test_unauthorized_user_can_not_edit_playlist(self):
        response = self.client.patch(
            reverse('playlists-detail', args=(self.other_playlist.playlist_id,)),
            {"name": "changed"}
        )
        self.assertForbidden(response)

    def test_unauthorized_user_can_not_create_playlist_item(self):
        collection_item = factories.HarikathaCollectionFactory()
        response = self.client.post(
            url_with_query_string(reverse('items-list'), {'playlist_id': self.other_playlist.playlist_id}),
            {"collection_item": collection_item.pk}
        )
        self.assertForbidden(response)

    def test_unauthorized_user_can_not_update_playlist_item(self):
        item = self.other_playlist.items.first()
        new_order = 2
        response = self.client.patch(
            reverse('items-detail', args=(item.item_id,)),
            {"new_order": new_order}
        )
        self.assertForbidden(response)

    def test_unauthorized_user_can_not_delete_playlist_item(self):
        item = self.other_playlist.items.first()
        response = self.client.delete(reverse('items-detail', args=(item.item_id,)))
        self.assertForbidden(response)


class TestHarikathaCollectionAdmin(BaseTestCase):

    def add_permission(self, user, category):
        permission = Permission.objects.get(codename='write_{}'.format(category))
        user.user_permissions.add(permission)

    def test_admin_form_has_correct_choices(self):
        """category field should have choices based on user permissions"""
        self.add_permission(self.user, 'harikatha')
        form = HariKathaCollectionForm(current_user=self.user)
        self.assertEqual(form.fields['category'].choices[0][0], 'harikatha')
