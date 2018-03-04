
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Date, Text, Completion, analyzer, token_filter
from . import models

connections.create_connection()

# es = Elasticsearch()
# es.indices.close(index='harikatha-index')
# es.indices.delete(index='harikatha-index')

# print(es.indices.get_mapping(index='harikatha-index'))

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
    title = Text()
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
    # HarikathaIndex.init()
    es = Elasticsearch()
    bulk(client=es, actions=(item.indexing() for item in models.HarikathaCollection.objects.all().iterator()))


# HarikathaIndex.init()
# es.indices.open(index='harikatha-index')
# item = HarikathaIndex(
#     meta={"id": 1},
#     title="this title",
#     title_suggest={"input": "this title", "contexts": {"category_type": "category here"}},
#     link="link here",
#     category="category here",
#     phrase_suggest="this title"
# )
# item.save()
# item.delete()

# es.indices.open(index="harikatha-index")
# print(HarikathaIndex.search().execute())
# s = HarikathaIndex.search()
# print(s.execute())
# s = s.suggest(
#     'other_suggestions',
#     'thsi tite',
#     phrase={
#         'field': 'phrase_suggest',
#         "max_errors": 2,
#     }
# )
# s = s.suggest(
#     'other_suggestions',
#     'this',
#     completion={
#         "field": "title_suggest",
#         "contexts": {
#             "category_type": "category here"
#         }
#     }
# )
# print(s.execute().suggest.other_suggestions)
# print(item)
