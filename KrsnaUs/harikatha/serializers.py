
from rest_framework import serializers
from collections import OrderedDict

from .models import HarikathaCollection


class HarikathaItem(serializers.ModelSerializer):
    """Serializer for HarikathaCollection model"""

    class Meta:
        model = HarikathaCollection
        exclude = ('id', 'indexed')

    def to_representation(self, instance):
        """Remove null fields from serializer"""
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


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
