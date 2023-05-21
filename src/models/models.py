from pydantic import Field

from models.mixins import ORJSONMixin, UUIDMixin


class FilmShort(UUIDMixin, ORJSONMixin):
    """A model to retrieve brief information on a film.

    """
    title: str
    imdb_rating: float | None


class Genre(UUIDMixin, ORJSONMixin):
    """A model to retrieve information on a genre.

    """
    name: str
    description: str | None


class Person(UUIDMixin, ORJSONMixin):
    """A model to retrieve information on a person.

    """
    name: str | None


class FilmFull(FilmShort):
    """A model to retrieve detailed information on a film.

    """
    description: str | None
    genres: list[Genre] | None = Field(default=[])
    actors: list[Person] | None = Field(default=[])
    writers: list[Person] | None = Field(default=[])
    directors: list[Person] | None = Field(default=[])
