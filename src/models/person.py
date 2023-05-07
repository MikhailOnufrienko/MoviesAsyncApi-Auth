import orjson

from pydantic import BaseModel

from models.film import FilmPersonRoles


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class PersonShort(BaseModel):
    """A model to retrieve information on a person.

    """
    full_name: str


class PersonFull(BaseModel):
    """A model to retrieve information on a person and his roles in films.

    """
    full_name: str
    films: list[FilmPersonRoles]
