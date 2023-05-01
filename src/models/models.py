from pydantic import Field

from src.models.mixins import ORJSONMixin, TimestampedMixin, UUIDMixin


class FilmShort(UUIDMixin, ORJSONMixin):
    title: str
    imdb_rating: float
    

class Genre(UUIDMixin, ORJSONMixin):
    title: str
    description: str


class Person(UUIDMixin, ORJSONMixin):
    full_name: str | None


class FilmFull(FilmShort):
    description: str | None
    genre: list[str] | None = Field(default=[])
    actors: list[Person] | None = Field(default=[])
    writers: list[Person] | None = Field(default=[])
    director: list[str] | None = Field(default=[])

