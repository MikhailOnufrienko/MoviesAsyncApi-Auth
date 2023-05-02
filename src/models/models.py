from pydantic import Field

from src.models.mixins import ORJSONMixin, TimestampedMixin, UUIDMixin


class FilmShort(UUIDMixin, ORJSONMixin):
    title: str
    imdb_rating: float
    

class Genre(UUIDMixin, ORJSONMixin):
    name: str
    description: str | None


class Person(UUIDMixin, ORJSONMixin):
    name: str | None


class FilmFull(FilmShort):
    description: str | None
    genre: list[Genre] | None = Field(default=[])
    actors: list[Person] | None = Field(default=[])
    writers: list[Person] | None = Field(default=[])
    director: list[Person] | None = Field(default=[])

