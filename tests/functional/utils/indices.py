settings_index = {
  "settings": {
    "refresh_interval": "1s",
    "analysis": {
      "filter": {
          "english_stop": {
              "type": "stop",
              "stopwords": "_english_"
          },
          "english_stemmer": {
             "type": "stemmer",
             "language": "english"
          },
          "english_possessive_stemmer": {
             "type": "stemmer",
             "language": "possessive_english"
          },
          "russian_stop": {
             "type": "stop",
             "stopwords": "_russian_"
          },
          "russian_stemmer": {
             "type": "stemmer",
             "language": "russian"
          }
       },
      "analyzer": {
          "ru_en": {
             "tokenizer": "standard",
             "filter": [
                "lowercase",
                "english_stop",
                "english_stemmer",
                "english_possessive_stemmer",
                "russian_stop",
                "russian_stemmer"
             ]
          }
       }
        }
     }
}

persons_index = {
  **settings_index,
  "mappings": {
    "dynamic": "strict",
    "properties": {
       "id": {
          "type": "keyword"
       },
       "full_name": {
          "type": "text",
          "analyzer": "ru_en"
       }
      }
   }
}

genres_index = {
    **settings_index,
    "mappings": {
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "description": {
            "type": "text",
            "analyzer": "ru_en"
          },
          "name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
    }
}

index_to_schema = {
    "persons": persons_index,
    "genres": genres_index
}