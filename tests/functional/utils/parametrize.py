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
