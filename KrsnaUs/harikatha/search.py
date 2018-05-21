
import os
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.exceptions import IllegalOperation
from elasticsearch_dsl import DocType, Text, Completion, analyzer, token_filter
from . import models


def get_connection_info():
    return 'http://{}:{}@elasticsearch/'.format(
        os.getenv('ES_NAME', 'elastic'), os.getenv('ELASTIC_PASSWORD', 'changeme')
    )


connections.create_connection(
    hosts=[get_connection_info()]
)

stop_word_filter = token_filter('stop_word_filter', type='stop', stopwords='_english_')
my_filter = token_filter('my_filter', type='shingle', min_shingle_size=2, max_shingle_size=3)
# used in "phrase_suggest" in HarikathaIndex
my_analysis = analyzer('my_analysis',
                       tokenizer="standard",
                       filter=[my_filter, stop_word_filter]
                       )

content_analysis = analyzer('content_analysis',
                            tokenizer='standard',
                            filter=['lowercase', stop_word_filter, 'asciifolding'])

content_suggestion_analysis = analyzer('content_suggestion_analysis',
                                       tokenizer='standard',
                                       filter=[my_filter, 'asciifolding']
                                       )


class HarikathaIndex(DocType):
    title = Text(analyzer=content_analysis)
    title_suggest = Completion(contexts=[{"name": "category_type", "type": "category"}])
    phrase_suggest = Text(analyzer=my_analysis)
    body = Text(analyzer=content_analysis)
    body_suggest = Text(analyzer=content_suggestion_analysis)
    link = Text()
    category = Text()
    language = Text()
    year = Text()
    issue = Text()
    directory = Text()
    page = Text()
    timestamp = Text()
    item_id = Text()
    content_title = Text()

    class Meta:
        index = 'harikatha-index'


def bulk_indexing():
    # create index if it doesn't exist
    try:
        HarikathaIndex.init()
    except IllegalOperation:
        pass
    es = Elasticsearch(hosts=[get_connection_info()])
    bulk(client=es, actions=(item.indexing() for item in models.HarikathaCollection.objects.all().iterator()))
