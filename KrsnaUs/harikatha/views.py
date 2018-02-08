
import requests
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_framework import generics, permissions
from rest_framework.views import APIView, Response
from rest_auth.registration.views import SocialLoginView
from .models import HarikathaCollection
from .serializers import HarikathaItem, Suggestion, ElasticsearchItem
from .search import HarikathaIndex
from .utils import PaginatedQuery

# Create your views here.

CATEGORIES = ["book", "movie", "song", "harikatha",
              "harmonistmonthly", "harmonistmagazine", "lecture", "bhagavatpatrika"
              ]


def get_query(categories, query):
    """Return elastic search query with filter if not all categories are in list else no filter"""
    if len(categories) == len(CATEGORIES) or len(categories) == 0:
        return HarikathaIndex.search().query('match', title=query)
    else:
        return HarikathaIndex.search().filter('terms', category=[category for category in categories]).query('match', title=query)


def add_suggestion(elastic_query, search_word):
    """Add suggestions to elastic search query and return"""
    return elastic_query.suggest(
            'other_suggestions',
            search_word,
            phrase={
                'field': 'phrase_suggest',
                "max_errors": 2,
            }
        )


class AccountConfirm(APIView):
    """View to verify email address"""

    def get(self, request, key, *args, **kwargs):
        """Make post request to verify_email endpoint"""
        r = requests.post('http://127.0.0.1:8000/rest-auth/registration/verify-email/', data={'key': key})
        return Response()


class PlayListsView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response({'authenticated': request.user.username})


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


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
        results = search_query.execute()
        response = {
            "nextPage": paged_query.next_page,
            "results": ElasticsearchItem(results.hits, many=True).data,
            "suggestions": Suggestion(results.suggest.other_suggestions[0]['options'], many=True).data
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
        # print(search.execute_suggest().title_complete[0]['options'][-1]['text'])
        return Response(Suggestion(search.execute_suggest().title_complete[0]['options'], many=True).data)
