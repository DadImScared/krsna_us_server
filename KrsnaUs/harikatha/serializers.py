
from rest_framework import serializers
from collections import OrderedDict

from .models import HarikathaCollection, Playlists, PlaylistItem


class HarikathaItem(serializers.ModelSerializer):
    """Serializer for HarikathaCollection model"""

    class Meta:
        model = HarikathaCollection
        exclude = ('id', 'indexed')

    def to_representation(self, instance):
        """Remove null fields from serializer"""
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class PlaylistItemSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='collection_item.title', read_only=True)
    link = serializers.CharField(source='collection_item.link', read_only=True)
    category = serializers.CharField(source='collection_item.category', read_only=True)

    class Meta:
        model = PlaylistItem
        fields = ('title', 'link', 'category', 'item_id', 'collection_item', 'item_order')
        read_only_fields = ('item_order',)
        extra_kwargs = {
            'collection_item': {'write_only': True}
        }


class PlaylistItemUpdateSerializer(serializers.ModelSerializer):

    new_order = serializers.IntegerField(source='item_order', write_only=True, required=True)

    class Meta:
        model = PlaylistItem
        fields = ('new_order',)

    def validate_new_order(self, value):
        """Validates the new order of the item and ensures it's in the constrains of all playlist items"""
        max_value = self.instance.playlist.items.count()
        if value > max_value:
            return max_value - 1
        elif value < 0:
            return 0
        else:
            return value


class PlaylistsSerializer(serializers.ModelSerializer):
    """serializer for Playlists model"""

    items_count = serializers.IntegerField(
        source='items.count',
        read_only=True
    )

    class Meta:
        model = Playlists
        fields = ('playlist_id', 'name', 'items_count')


class PlaylistWithItemsSerializer(PlaylistsSerializer):

    items = PlaylistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Playlists
        fields = PlaylistsSerializer.Meta.fields + ('items',)


class ElasticsearchItem(serializers.Serializer):
    """Serializer for elastic search document"""
    title = serializers.CharField()
    highlightedTitle = serializers.SerializerMethodField(source='meta.highlight.title')
    link = serializers.CharField()
    category = serializers.CharField()
    year = serializers.CharField()
    issue = serializers.CharField()
    directory = serializers.CharField()
    language = serializers.CharField()

    def get_highlightedTitle(self, obj):
        return obj.meta.highlight.title[0]

    def to_representation(self, instance):
        """Remove null fields from serializer"""
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class Suggestion(serializers.Serializer):
    # score is used for phrase suggestion not auto complete suggestion need to split into two classes
    # commenting out score for now to work on client of auto complete
    # score = serializers.FloatField(allow_null=True)
    text = serializers.CharField()


class SearchResponseSerializer(serializers.Serializer):
    results = ElasticsearchItem(many=True, required=True)
    suggestions = Suggestion(many=True, required=True)
