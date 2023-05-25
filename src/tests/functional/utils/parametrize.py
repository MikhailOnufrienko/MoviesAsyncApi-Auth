from http import HTTPStatus


FILM_QUERY_EXIST = 'The Star'
FILM_QUERY_NOT_EXIST = 'Film Not-Exist'

PERSON_SINGLE_QUERY_EXIST = 'Single Name'
PERSON_MULTIPLE_QUERY_EXIST = 'Multiple Name'
PERSON_QUERY_NOT_EXIST = 'Person Not-Exist'


film_search_parameters = [
    (
        {
            'query': FILM_QUERY_EXIST,
            'page_number': 1,
            'page_size': 10
        },
        {
            'status': 200,
            'length': 50,
            'has_next_page': True
        }
    ),
    (
        {
            'query': FILM_QUERY_NOT_EXIST,
            'page_number': 1,
            'page_size': 10
        },
        {
            'status': 200,
            'length': 0,
            'has_next_page': False
        }
    )
]


films_by_genre_parameters = [
    (
        '120a21cf-9097-479e-904a-13dd7198c1dd',
        {
            'genre': '120a21cf-9097-479e-904a-13dd7198c1dd',
            'page_number': 1,
            'page_size': 10
        },
        {
            'status': 200,
            'length': 50,
            'has_next_page': True
        }
    ),
    (
        '111a11a1-1111-111a-111a-11aa1111a1aa',
        {
            'genre': '111a11a1-1111-111a-111a-11aa1111a1aa',
            'page_number': 1,
            'page_size': 10
        },
        {
            'status': 200,
            'length': 0,
            'has_next_page': False
        }
    )
]


film_detail_parameters = [
    (
        'b8076788-de5b-426a-b78b-08e9dc819841',
        {
            'status': HTTPStatus.OK,
            'response_body': {
                'id': 'b8076788-de5b-426a-b78b-08e9dc819841',
                'title': FILM_QUERY_EXIST,
                'imdb_rating': 8.5,
                'description': 'New World',
                'genres': [
                    {
                        'id': '120a21cf-9097-479e-904a-13dd7198c1dd',
                        'name': 'Adventure',
                        'description': 'Exciting and unusual experience.'
                    }
                ],
                'actors': [
                    {
                        'id': '32b50c6b-4907-292f-b652-6ef2ee8b43f8',
                        'name': PERSON_SINGLE_QUERY_EXIST
                    },
                    {'id': '222', 'name': 'Bob'}
                ],
                'writers': [
                    {'id': '333', 'name': 'Ben'},
                    {'id': '444', 'name': 'Howard'}
                ],
                'directors': [
                    {
                        'id': 'a0077238-c960-4c22-9824-e49d8585cf3d',
                        'name': 'Main Director'
                    }
                ],
            }
        },
    ),
    (
        '111a11a1-1111-111a-111a-11aa1111a1aa',
        {
            'status': HTTPStatus.NOT_FOUND,
            'response_body': {
                'detail': 'Film not found',
            }
        },
    )
]


film_detail_cache_parameters = [
    (
        'b8076788-de5b-426a-b78b-08e9dc819841',
        {
            'id': 'b8076788-de5b-426a-b78b-08e9dc819841',
            'title': 'The Star',
            'imdb_rating': 8.5,
            'description': 'New World',
            'genres': [
                {
                    'id': '120a21cf-9097-479e-904a-13dd7198c1dd',
                    'name': 'Adventure',
                }
            ],
            'actors': [
                {
                    'id': '32b50c6b-4907-292f-b652-6ef2ee8b43f8',
                    'name': PERSON_SINGLE_QUERY_EXIST
                },
                {
                    'id': '222',
                    'name': 'Bob'
                }
            ],
            'writers': [
                {
                    'id': '333',
                    'name': 'Ben'
                },
                {
                    'id': '444',
                    'name': 'Howard'
                }
            ],
            'directors': [
                {
                    'id': 'a0077238-c960-4c22-9824-e49d8585cf3d',
                    'name': 'Main Director'
                }
            ]
        }
    )
]


person_search_parameters = [
    (
        {
            'query': PERSON_SINGLE_QUERY_EXIST,
            'page_number': 1,
            'page_size': 10
        },
        {
            'status': 200,
            'length': 1,
            'has_next_page': False
        }
    ),
    (
        {
            'query': PERSON_MULTIPLE_QUERY_EXIST,
            'page_number': 1,
            'page_size': 10
        },
        {
            'status': 200,
            'length': 20,
            'has_next_page': True
        }
    ),
    (
        {
            'query': PERSON_QUERY_NOT_EXIST,
            'page_number': 1,
            'page_size': 10
        },
        {
            'status': 200,
            'length': 0,
            'has_next_page': False
        }
    )
]


person_films_parameters = [
    (
        '32b50c6b-4907-292f-b652-6ef2ee8b43f8',
        {
            'status': 200,
            'length': 50,
            'body_length': 10,
        }
    ),
    (
        '22b22b2b-2222-222b-b222-2bb2bb2b22b2',
        {
            'status': 404,
            'length': 0,
            'body_length': 0,
        }
    )
]


person_detail_parameters = [
    (
        '32b50c6b-4907-292f-b652-6ef2ee8b43f8',
        {
            'status': 200,
            'id': '32b50c6b-4907-292f-b652-6ef2ee8b43f8',
            'full_name': PERSON_SINGLE_QUERY_EXIST,
            'length': 10
        }
    ),
    (
        '22b22b2b-2222-222b-b222-2bb2bb2b22b2',
        {
            'status': 404,
            'id': '22b22b2b-2222-222b-b222-2bb2bb2b22b2',
            'full_name': PERSON_QUERY_NOT_EXIST,
            'length': 0,
        }
    )
]


genre_detail_parameters = [
    (
        '120a21cf-9097-479e-904a-13dd7198c1dd',
        {
            'status': HTTPStatus.OK,
            'response_body': {
                'name': 'Adventure',
                'id': '120a21cf-9097-479e-904a-13dd7198c1dd'
            }
        },
    ),
    (
        '111a11a1-1111-111a-111a-11aa1111a1aa',
        {
            'status': HTTPStatus.NOT_FOUND,
            'response_body': {
                'detail': 'Genre not found',
            }
        },
    )
]
