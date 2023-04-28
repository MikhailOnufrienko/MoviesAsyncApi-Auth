from pydantic import Field

from .mixins import ORJSONMixin, TimestampedMixin, UUIDMixin


class FilmShort(UUIDMixin, TimestampedMixin, ORJSONMixin):
    title: str
    imdb_rating: float
    

class Genre(UUIDMixin, TimestampedMixin, ORJSONMixin):
    title: str
    description: str


class Person(UUIDMixin, TimestampedMixin, ORJSONMixin):
    full_name: str


class FilmFull(FilmShort):
    description: str | None
    genre: list[str] | None = Field(default=[])
    actors: list[Person] | None = Field(default=[])
    writers: list[Person] | None = Field(default=[])
    director: list[str] | None = Field(default=[])

