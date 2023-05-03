import orjson

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Film(BaseModel):
    id: str
    title: str
    description: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PersonShortFilm(BaseModel):
    uuid: str
    roles: list


class PersonShortFilmInfo(BaseModel):
    uuid: str
    title: str
    imdb_rating: float
