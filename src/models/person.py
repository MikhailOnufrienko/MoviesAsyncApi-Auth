import orjson

from pydantic import BaseModel

from models.film import FilmPersonRoles


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class PersonShort(BaseModel):
    id: str
    full_name: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PersonFull(BaseModel):
    id: str
    full_name: str
    films: list[FilmPersonRoles]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
