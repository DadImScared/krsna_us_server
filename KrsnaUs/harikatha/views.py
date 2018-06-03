
import requests
import collections
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django.db.models import F
from django.http import HttpResponseRedirect
from django.conf import settings
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import list_route
from rest_framework.reverse import reverse
from rest_framework.views import APIView, Response
from rest_auth.registration.views import SocialLoginView

from .models import HarikathaCollection, Playlists, PlaylistItem
from .serializers import (
    HarikathaItem,
    Suggestion,
    ElasticsearchItem,
    PlaylistsSerializer,
    PlaylistItemSerializer,
    PlaylistItemUpdateSerializer,
    PlaylistWithItemsSerializer,
    PlaylistsHasItemSerializer,
    ReSendEmailSerializer
)
from .search import HarikathaIndex
from .utils import PaginatedQuery
from .my_permissions import CanWriteOrDeletePlaylist, CanWriteOrDeletePlaylistItem

# Create your views here.

CATEGORIES = ["book", "movie", "song", "harikatha",
              "harmonistmonthly", "harmonistmagazine", "lecture", "bhagavatpatrika"
              ]


def get_query(categories, query):
    """Return elastic search query with filter if not all categories are in list else no filter"""
    if len(categories) == len(CATEGORIES) or len(categories) == 0:
        return HarikathaIndex.search().query('multi_match', query=query, fields=['title', 'body'])
    else:
        return HarikathaIndex.search().filter(
            'terms', category=[category for category in categories]
        ).query('multi_match', query=query, fields=['title', 'body'])


def add_suggestion(elastic_query, search_word):
    """Add suggestions to elastic search query"""
    return elastic_query.suggest(
            'other_suggestions',
            search_word,
            phrase={
                'field': 'phrase_suggest',
                "max_errors": 2,
            }
        ).suggest(
        'body_suggestions',
        search_word,
        phrase={
            'field': 'body_suggest',
            'max_errors': 2
        }
    )


def combine_suggestions(title_suggestions, body_suggestions):
    """Combines and removes duplicate suggestions from title suggestions and body_suggestions and sorts by score

    :param list title_suggestions: List of elastic search suggestions
    :param list body_suggestions:  List of elastic search suggestions
    :return list: List of combined unique suggestions sorted by score
    """
    return {
        suggestion['text']: suggestion for suggestion in
        sorted([*title_suggestions, *body_suggestions], key=lambda obj: obj['score'], reverse=True)
    }.values()


class ReSendEmailConfirm(APIView):

    def post(self, request, *args, **kwargs):
        serializer = ReSendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = email.user
        send_email_confirmation(request, user)
        return Response({"message": "Email confirmation sent"})


class AccountConfirm(APIView):
    """View to verify email address"""

    def get(self, request, key, *args, **kwargs):
        """Make post request to verify_email endpoint"""
        requests.post(request.build_absolute_uri(reverse('rest_verify_email')), data={'key': key})
        return HttpResponseRedirect(settings.CLIENT_URL)


class PlaylistsViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistsSerializer
    lookup_field = 'playlist_id'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, CanWriteOrDeletePlaylist)

    def get_queryset(self):
        """Returns all Playlist objects if user is not authenticated else Playlist objects created by user"""
        if not self.request.user.is_authenticated and self.action == 'list':
            return []
        elif self.request.user.is_authenticated and self.action == 'list':
            return Playlists.objects.filter(creator=self.request.user)
        return Playlists.objects.all()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @list_route()
    def all_playlists(self, request):
        all_playlists = Playlists.objects.all()
        page = self.paginate_queryset(all_playlists)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(all_playlists, many=True)
        return Response(serializer.data)

    @list_route(permission_classes=[permissions.IsAuthenticated])
    def has_item(self, request):
        item_id = request.query_params.get('item_id', None)
        playlists = Playlists.objects.filter(creator=request.user)
        serializer = PlaylistsHasItemSerializer(playlists, many=True, context={'item_id': item_id})
        return Response(serializer.data)


class PlaylistItemsViewSet(viewsets.ModelViewSet):
    queryset = PlaylistItem.objects.all()
    serializer_class = PlaylistItemSerializer
    lookup_field = 'item_id'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, CanWriteOrDeletePlaylistItem)

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return PlaylistItemUpdateSerializer
        return PlaylistItemSerializer

    def list(self, request, *args, **kwargs):
        playlist = Playlists.objects.get(playlist_id=request.query_params.get('playlist_id'))
        serializer = PlaylistWithItemsSerializer(
            instance=playlist,
            context={'playlist': playlist, 'request': request}
        )
        return Response(serializer.data)

    def perform_create(self, serializer):
        playlist = Playlists.objects.get(
            creator=self.request.user,
            playlist_id=self.request.query_params.get('playlist_id')
        )
        serializer.save(playlist=playlist, item_order=PlaylistItem.objects.filter(playlist=playlist).count())

    def partial_update(self, request, *args, **kwargs):
        playlist = self.get_object().playlist
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid()
        current_order = self.get_object().item_order
        new_order = request.data['new_order']
        queryset = self.get_queryset()
        if int(new_order) < current_order:
            items = queryset.filter(playlist=playlist, item_order__lt=current_order, item_order__gte=new_order)
            items.update(item_order=F('item_order') + 1)
        else:
            queryset.filter(
                playlist=playlist,
                item_order__gt=current_order,
                item_order__lte=new_order
            ).update(item_order=F('item_order') - 1)
        serializer.save()
        return Response(PlaylistItemSerializer(instance=self.get_object()).data)

    def destroy(self, request, *args, **kwargs):
        item_order = self.get_object().item_order
        playlist = self.get_object().playlist
        response = super().destroy(request, *args, **kwargs)
        queryset = self.queryset
        queryset.filter(
            playlist=playlist,
            item_order__gt=item_order
        ).update(item_order=F('item_order') - 1)
        return response


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class AllItemsView(APIView):
    """View that displays all items not made for a client but for backend tools"""

    def get(self, request):
        queryset = HarikathaCollection.objects
        data = {
            "books": HarikathaItem(queryset.filter(category='book'),  many=True).data,
            "movies": HarikathaItem(queryset.filter(category='movie'), many=True).data,
            "lectures": HarikathaItem(queryset.filter(category='lecture'), many=True).data,
            "songs": HarikathaItem(queryset.filter(category='song'), many=True).data,
            "bhagavatpatrika": HarikathaItem(queryset.filter(category='bhagavatpatrika'), many=True).data,
            "harikatha": HarikathaItem(queryset.filter(category='harikatha'), many=True).data,
            "harmonistmagazine": HarikathaItem(queryset.filter(category='harmonistmagazine'), many=True).data,
            "harmonistmonthly": HarikathaItem(queryset.filter(category='harmonistmonthly'), many=True).data
        }
        return Response(data)


class AllItemsSearchView(APIView):

    def get(self, request, query: str):
        plurals = ['movie', 'song', 'lecture', 'book']
        query = query
        queryset = HarikathaCollection.objects.filter(title__icontains=query)
        data = collections.defaultdict(list)
        for item in queryset:
            data[item.category + 's' if item.category in plurals else item.category].append(HarikathaItem(item).data)
        return Response(data)


class HariKathaCollectionView(generics.ListAPIView):
    """View to display items from HarikathaCollection"""
    serializer_class = HarikathaItem

    def get_queryset(self):
        """Filter items based on categories query string"""
        categories = self.request.query_params.getlist('categories', CATEGORIES).lower()
        return HarikathaCollection.objects.filter(category__in=[category for category in categories])


class HariKathaCategoryView(generics.ListAPIView):

    serializer_class = HarikathaItem

    def get_queryset(self):
        """Filter items based on category url parameter"""
        return HarikathaCollection.objects.filter(category=self.kwargs["category"].lower())


class HariKathaCollectionSearch(APIView):
    """Search endpoint for elastic search collection"""

    def get(self, request, query):
        """Query elastic search and return serialized results

        :param object request: Django rest framework Request object
        :param str query: Search query
        :return: Response object with serializer.data set to SearchResultSerializer object

        """
        categories = request.query_params.getlist('categories', CATEGORIES)
        search_query = get_query(categories, query)
        paged_query = PaginatedQuery(
            search_query,
            '/api/v1/search/{}'.format(query),
            request.GET.urlencode(),
            page_number=request.query_params.get('page', 1)
        )
        search_query = paged_query.query
        search_query = add_suggestion(search_query, query)
        search_query = search_query.highlight('title')
        search_query = search_query.highlight('body', fragment_size=200)
        results = search_query.execute()
        response = {
            "nextPage": paged_query.next_page,
            "results": ElasticsearchItem(results.hits, many=True).data,
            "suggestions": Suggestion(
                combine_suggestions(
                    results.suggest.other_suggestions[0]['options'],
                    results.suggest.body_suggestions[0]['options']
                ), many=True
            ).data
        }
        return Response(response)


class HariKathaCollectionAutoComplete(APIView):
    def get(self, request, query):
        """Auto complete search query"""
        categories = request.query_params.getlist('categories', CATEGORIES)
        search = HarikathaIndex.search()
        search = search.suggest(
            'title_complete',
            query,
            completion={
                "field": "title_suggest",
                "contexts": {
                    "category_type": [category for category in categories]
                }
            }
        )
        return Response(Suggestion(search.execute().suggest.title_complete[0]['options'], many=True).data)
