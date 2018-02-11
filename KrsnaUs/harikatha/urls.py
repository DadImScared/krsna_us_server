
from django.conf.urls import url, include
from rest_framework import routers

from .views import (
    HariKathaCollectionSearch,
    HariKathaCollectionAutoComplete,
    HariKathaCategoryView,
    PlaylistsViewSet,
    PlaylistItemsViewSet
)

router = routers.SimpleRouter()
router.register(r'playlists', PlaylistsViewSet, base_name='playlists')
router.register(r'items', PlaylistItemsViewSet, base_name='items')

urlpatterns = [
    url(r'^items/(?P<category>[a-zA-Z]+)/$', HariKathaCategoryView.as_view(), name='items'),
    url(r'^search/(?P<query>[\w. ]+)/$', HariKathaCollectionSearch.as_view(), name="search-items"),
    url(r'^completeme/(?P<query>[\w. ]+)/$', HariKathaCollectionAutoComplete.as_view(), name="auto-complete"),
    url(r'^', include(router.urls))
]
