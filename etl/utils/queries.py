from .settings import etl_settings


def get_modified_genres(timestamp: int) -> str:
    """A query to get genres which were
    modified during the given period of time.

    """
    return """
        SELECT id, modified
        FROM content.genre
        WHERE modified > '{}'
        ORDER BY modified
        LIMIT {};
        """.format(timestamp, etl_settings.LIMIT)


def get_modified_persons(timestamp) -> str:
    """A query to get persons which were
    modified during the given period of time.

    """
    return """
        SELECT id, modified
        FROM content.person
        WHERE modified > '{}'
        ORDER BY modified
        LIMIT {};
        """.format(timestamp, etl_settings.LIMIT)


def get_modified_filmworks(timestamp) -> str:
    """A query to get filmworks which were
    modified during the given period of time.

    """
    return """
        SELECT id, modified
        FROM content.film_work
        WHERE modified > '{}'
        ORDER BY modified
        LIMIT {};
        """.format(timestamp, etl_settings.LIMIT)


def get_modified_filmworks_by_persons(persons: list) -> str:
    """A query to get filmworks which have persons modified.

    """
    condition = f'IN {tuple(persons)}' if len(
        persons) > 1 else f'= "{persons[0]}"'
    return """
    SELECT fw.id, fw.modified
    FROM content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    WHERE pfw.person_id {}
    ORDER BY fw.modified;
    """.format(condition)


def get_modified_filmworks_by_genres(genres: list) -> str:
    """A query to get filmworks which have genres modified.

    """
    condition = f'IN {tuple(genres)}' if len(
        genres) > 1 else f'= "{genres[0]}"'
    return """
    SELECT fw.id, fw.modified
    FROM content.film_work fw
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    WHERE gfw.genre_id {}
    ORDER BY fw.modified;
    """.format(condition)


def get_filmwork_by_id(ids: tuple) -> str:
    """A query to get modified filmworks and their attributes.

    """
    condition = f'IN {tuple(ids)}' if len(ids) > 1 else f'= "{ids[0]}"'
    return """
        SELECT
            fw.id as fw_id,
            fw.title,
            fw.description,
            fw.rating,
            fw.type,
            fw.created,
            fw.modified,
            pfw.role,
            p.id as person_id,
            p.full_name,
            g.name as genre
        FROM content.film_work fw
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
        LEFT JOIN content.person p ON p.id = pfw.person_id
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
        LEFT JOIN content.genre g ON g.id = gfw.genre_id
        WHERE fw.id {};
        """.format(condition)


def get_genres(timestamp) -> str:
    """A query to get genres modified.

    """
    return """
        SELECT 
            genre.id, 
            genre.name, 
            genre.description,
            genre.modified, 
            ARRAY_AGG(DISTINCT jsonb_build_object(
                'id', film.id, 'title', film.title, 'imdb_rating', film.rating
            ))
        FROM content.genre genre 
        LEFT JOIN content.genre_film_work as genre_film on genre.id = genre_film.genre_id 
        LEFT JOIN content.film_work AS film on genre_film.film_work_id = film.id 
        WHERE genre.modified > '{}'
        GROUP BY genre.id
        ORDER by genre.modified;
        """.format(timestamp)


