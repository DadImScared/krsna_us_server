
from django.shortcuts import get_object_or_404
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
    collection_item = serializers.CharField(source='collection_item.item_id', write_only=True)

    class Meta:
        model = PlaylistItem
        fields = ('title', 'link', 'category', 'item_id', 'collection_item', 'item_order')
        read_only_fields = ('item_order',)
        extra_kwargs = {
            'collection_item': {'write_only': True}
        }

    def validate_collection_item(self, value):
        try:
            PlaylistItem.objects.get(
                playlist__playlist_id=self.context['request'].query_params.get('playlist_id'),
                collection_item__item_id=value
            )
        except PlaylistItem.DoesNotExist:
            return value
        else:
            raise serializers.ValidationError('Playlist has item already')

    def create(self, validated_data):
        collection_item = validated_data.pop('collection_item')
        hk_item = get_object_or_404(HarikathaCollection, item_id=collection_item['item_id'])
        return PlaylistItem.objects.create(collection_item=hk_item, **validated_data)


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


class PlaylistsHasItemSerializer(PlaylistsSerializer):

    hasItem = serializers.SerializerMethodField(method_name='get_has_item')

    class Meta:
        model = Playlists
        fields = PlaylistsSerializer.Meta.fields + ('hasItem',)

    def get_has_item(self, obj):
        """Return True if playlist has item else False"""
        item_id = self.context['item_id']
        try:
            return obj.items.get(collection_item__item_id=item_id).item_id
        except PlaylistItem.DoesNotExist:
            return False


class PlaylistWithItemsSerializer(PlaylistsSerializer):

    items = PlaylistItemSerializer(many=True, read_only=True)
    isCreator = serializers.SerializerMethodField(method_name='is_creator')

    class Meta:
        model = Playlists
        fields = PlaylistsSerializer.Meta.fields + ('items', 'isCreator')

    def is_creator(self, obj):
        """Return True if user is creator of playlist else False"""
        playlist = self.context['playlist']
        user = self.context['request'].user
        return True if user.is_authenticated and playlist.creator == user else False


class ElasticsearchItem(serializers.Serializer):
    """Serializer for elastic search document"""
    title = serializers.SerializerMethodField()
    highlightedTitle = serializers.SerializerMethodField()
    highlightedBody = serializers.SerializerMethodField()
    link = serializers.CharField()
    category = serializers.CharField()
    year = serializers.CharField()
    issue = serializers.CharField()
    directory = serializers.CharField()
    language = serializers.CharField()
    item_id = serializers.CharField()

    def get_highlightedTitle(self, obj):
        if 'title' in obj.meta.highlight:
            return obj.meta.highlight['title'][0]
        return None

    def get_highlightedBody(self, obj):
        if 'body' in obj.meta.highlight:
            return obj.meta.highlight['body'][0]
        return None

    def get_title(self, obj):
        # content of magazines/books have book_title instead of title
        return obj.content_title if 'content_title' in obj else obj.title

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
