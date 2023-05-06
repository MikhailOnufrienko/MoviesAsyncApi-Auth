import uuid
from datetime import datetime

from pydantic import BaseModel


class UUIDMixin(BaseModel):
    id: str


class ModifiedMixin(BaseModel):
    modified: datetime


class PGFilmworkModel(UUIDMixin, ModifiedMixin):
    """A model for movies."""


class PGGenreModel(UUIDMixin, ModifiedMixin):
    """A model for movie genres."""


class PGPersonModel(UUIDMixin, ModifiedMixin):
    """A model for movie personnel."""


class PGGenreFilmworkModel(UUIDMixin, ModifiedMixin):
    """A model for movies by genre."""


class PGPersonFilmworkModel(UUIDMixin, ModifiedMixin):
    """A model for movies with specific persons."""


class ESPersonModel(UUIDMixin):
    """A model for Elasticsearch person instances."""
    name: str | None


class ESGenreAndFilmModel(UUIDMixin):
    name: str


class ESFilmworkModel(UUIDMixin):
    """A model for Elasticsearch filmwork instances."""
    imdb_rating: float | None
    genre: list[ESGenreAndFilmModel] | None
    title: str
    description: str | None
    director: list[ESPersonModel] | None
    actors_names: list[str] | None
    writers_names: list[str] | None
    actors: list[ESPersonModel] | None
    writers: list[ESPersonModel] | None


class PGGenreAndFilmModel(UUIDMixin, ModifiedMixin):
    name: str
    description: str | None


class Person(BaseModel):
    id: uuid.UUID
    full_name: str
