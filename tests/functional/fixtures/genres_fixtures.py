import uuid

import pytest


@pytest.fixture
def generate_es_data_genre():
    """Generate genre data.
    
    """
    genres = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Comedy',
                'description': 'Movies to make you laugh:)'
            }
            for _ in range(9)
        ]
    genres.append(
        {
            'id': '120a21cf-9097-479e-904a-13dd7198c1dd',
            'name': 'Adventure',
            'description': 'Exciting and unusual experience.'
        }
    )
    return genres
