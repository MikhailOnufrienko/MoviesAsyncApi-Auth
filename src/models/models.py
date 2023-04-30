from pydantic import Field

from src.models.mixins import ORJSONMixin, TimestampedMixin, UUIDMixin


class FilmShort(UUIDMixin, ORJSONMixin):
    title: str
    imdb_rating: float
    

class Genre(UUIDMixin, TimestampedMixin, ORJSONMixin):
    title: str
    description: str


class Person(UUIDMixin, TimestampedMixin, ORJSONMixin):
    full_name: str


class FilmFull(FilmShort):
    description: str | None
    genres: list[str] | None = Field(default=[])
    actors: list[Person] | None = Field(default=[])
    writers: list[Person] | None = Field(default=[])
    directors: list[str] | None = Field(default=[])

