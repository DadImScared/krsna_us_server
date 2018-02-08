
from django.conf.urls import url

from .views import HariKathaCollectionSearch, HariKathaCollectionAutoComplete, HariKathaCategoryView, PlayListsView

urlpatterns = [
    url(r'^items/(?P<category>[a-zA-Z]+)/$', HariKathaCategoryView.as_view(), name='items'),
    url(r'^search/(?P<query>[\w. ]+)/$', HariKathaCollectionSearch.as_view(), name="search-items"),
    url(r'^completeme/(?P<query>[\w. ]+)/$', HariKathaCollectionAutoComplete.as_view(), name="auto-complete"),
    url(r'^playlists/', PlayListsView.as_view(), name='playlists')
]
