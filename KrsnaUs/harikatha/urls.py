
from django.conf.urls import url, include
from rest_framework import routers

from .views import (
    HariKathaCollectionSearch,
    HariKathaCollectionAutoComplete,
    HariKathaCategoryView,
    PlaylistsViewSet,
    PlaylistItemsViewSet,
    ReSendEmailConfirm,
    AllItemsView,
    AllItemsSearchView
)

router = routers.SimpleRouter()
router.register(r'playlists', PlaylistsViewSet, base_name='playlists')
router.register(r'playlistitems', PlaylistItemsViewSet, base_name='items')

urlpatterns = [
    url(r'^items/(?P<category>[a-zA-Z]+)/$', HariKathaCategoryView.as_view(), name='items'),
    url(r'^all/$', AllItemsView.as_view(), name='all_items'),
    url(r'^all/search/(?P<query>[\w. \'-_]+)/$', AllItemsSearchView.as_view(), name='search-all-items'),
    url(r'^search/(?P<query>[\w. \'-_]+)/$', HariKathaCollectionSearch.as_view(), name="search-items"),
    url(r'^completeme/(?P<query>[\w. \'-_]+)/$', HariKathaCollectionAutoComplete.as_view(), name="auto-complete"),
    url(r'^resend_email/', ReSendEmailConfirm.as_view(), name='resend_email'),
    url(r'^', include(router.urls))
]
