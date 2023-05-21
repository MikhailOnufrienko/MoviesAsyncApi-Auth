
# BASE_INDEX_SETTINGS = {
#     'refresh_interval': '1s',
#     'analysis': {
#         'filter': {
#             'english_stop': {
#                 'type': 'stop',
#                 'stopwords': '_english_'
#             },
#             'english_stemmer': {
#                 'type': 'stemmer',
#                 'language': 'english'
#             },
#             'english_possessive_stemmer': {
#                 'type': 'stemmer',
#                 'language': 'possessive_english'
#             },
#             'russian_stop': {
#                 'type': 'stop',
#                 'stopwords': '_russian_'
#             },
#             'russian_stemmer': {
#                 'type': 'stemmer',
#                 'language': 'russian'
#             }
#         },
#         'analyzer': {
#             'ru_en': {
#                 'tokenizer': 'standard',
#                 'filter': [
#                     'lowercase',
#                     'english_stop',
#                     'english_stemmer',
#                     'english_possessive_stemmer',
#                     'russian_stop',
#                     'russian_stemmer'
#                 ]
#             }
#         }
#     }
# }


# MOVIES_INDEX_SETTINGS = {
#     'settings': BASE_INDEX_SETTINGS,
#     'mappings': {
#         'dynamic': 'strict',
#         'properties': {
#             'id': {
#                 'type': 'keyword'
#             },
#             'imdb_rating': {
#                 'type': 'float'
#             },
#             'genre': {
#                 'type': 'nested',
#                 'dynamic': 'strict',
#                 'properties': {
#                     'id': {
#                         'type': 'keyword'
#                     },
#                     'name': {
#                         'type': 'text',
#                         'analyzer': 'ru_en'
#                     },
#                     'description': {
#                         'type': 'text',
#                         'analyzer': 'ru_en'
#                     }
#                 }
#             },
#             'title': {
#                 'type': 'text',
#                 'analyzer': 'ru_en',
#                 'fields': {
#                     'raw': {
#                         'type': 'keyword'
#                     }
#                 }
#             },
#             'description': {
#                 'type': 'text',
#                 'analyzer': 'ru_en'
#             },
#             'director': {
#                 "type": "nested",
#                 "dynamic": "strict",
#                 'properties': {
#                     'id': {
#                         'type': 'keyword'
#                     },
#                     'name': {
#                         'type': 'text',
#                         'analyzer': 'ru_en'
#                     }
#                 }
#             },
#             'actors_names': {
#                 'type': 'text',
#                 'analyzer': 'ru_en'
#             },
#             'writers_names': {
#                 'type': 'text',
#                 'analyzer': 'ru_en'
#             },
#             'actors': {
#                 'type': 'nested',
#                 'dynamic': 'strict',
#                 'properties': {
#                     'id': {
#                         'type': 'keyword'
#                     },
#                     'name': {
#                         'type': 'text',
#                         'analyzer': 'ru_en'
#                     }
#                 }
#             },
#             'writers': {
#                 'type': 'nested',
#                 'dynamic': 'strict',
#                 'properties': {
#                     'id': {
#                         'type': 'keyword'
#                     },
#                     'name': {
#                         'type': 'text',
#                         'analyzer': 'ru_en'
#                     }
#                 }
#             }
#         }
#     }
# }


# GENRES_INDEX_SETTINGS = {
#     'settings': BASE_INDEX_SETTINGS,
#     'mappings': {
#         'dynamic': 'strict',
#         'properties': {
#             'id': {
#                 'type': 'keyword'
#             },
#             'name': {
#                 'type': 'text',
#                 'analyzer': 'ru_en'
#             },
#             'description': {
#                 'type': 'text',
#                 'analyzer': 'ru_en'
#             }

# settings_index = {
#   "settings": {
#     "refresh_interval": "1s",
#     "analysis": {
#       "filter": {
#           "english_stop": {
#               "type": "stop",
#               "stopwords": "_english_"
#           },
#           "english_stemmer": {
#              "type": "stemmer",
#              "language": "english"
#           },
#           "english_possessive_stemmer": {
#              "type": "stemmer",
#              "language": "possessive_english"
#           },
#           "russian_stop": {
#              "type": "stop",
#              "stopwords": "_russian_"
#           },
#           "russian_stemmer": {
#              "type": "stemmer",
#              "language": "russian"
#           }
#        },
#       "analyzer": {
#           "ru_en": {
#              "tokenizer": "standard",
#              "filter": [
#                 "lowercase",
#                 "english_stop",
#                 "english_stemmer",
#                 "english_possessive_stemmer",
#                 "russian_stop",
#                 "russian_stemmer"
#              ]
#           }
#        }
#         }
#      }
# }

# persons_index = {
#   **settings_index,
#   "mappings": {
#     "dynamic": "strict",
#     "properties": {
#        "id": {
#           "type": "keyword"
#        },
#        "full_name": {
#           "type": "text",
#           "analyzer": "ru_en"
#        }
#       }
#    }
# }

# genres_index = {
#     **settings_index,
#     "mappings": {
#         "dynamic": "strict",
#         "properties": {
#           "id": {
#             "type": "keyword"
#           },
#           "description": {
#             "type": "text",
#             "analyzer": "ru_en"
#           },
#           "name": {
#             "type": "text",
#             "analyzer": "ru_en"
#           }

#         }
#     }
# }



PERSONS_INDEX_SETTINGS = {
    'settings': BASE_INDEX_SETTINGS,
    'mappings': {
        'dynamic': 'strict',
        'properties': {
            'id': {
                'type': 'keyword'
            },
            'full_name': {
                'type': 'text',
                'analyzer': 'ru_en'
            }
        }
    }

index_to_schema = {
    "persons": persons_index,
    "genres": genres_index
}
