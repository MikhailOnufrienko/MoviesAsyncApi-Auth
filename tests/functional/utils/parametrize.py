from http import HTTPStatus


FILM_QUERY_EXIST = 'The Star'
FILM_QUERY_NOT_EXIST = 'Film Not-Exist'

PERSON_QUERY_EXIST = 'Random Name'
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
                    {'id': '111', 'name': 'Ann'},
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
            'genre': [
                {
                    'id': '120a21cf-9097-479e-904a-13dd7198c1dd',
                    'name': 'Adventure',
                }
            ],
            'actors': [
                {
                    'id': '111',
                    'name': 'Ann'
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
            'director': [
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
            'query': PERSON_QUERY_EXIST,
            'page_number': 1,
            'page_size': 10
        },
        {
            'status': 200,
            'length': 21,
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
