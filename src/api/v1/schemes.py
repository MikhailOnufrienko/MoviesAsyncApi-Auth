"""API models."""


from uuid import UUID
from pydantic import BaseModel, Field


class FilmShort(BaseModel):
    """An API model to represent brief film information.

    """
    id: str
    title: str
    imdb_rating: float | None


class FilmList(BaseModel):
    """An API model to represent a list of films with a paginator.

    """
    total: int
    page: int
    size: int | None
    prev: str | None
    next: str | None
    results: list[FilmShort]


class GenreInFilm(BaseModel):
    """An API model to represent genre information within FilmFull class.

    """
    id: str
    name: str
    description: str | None


class PersonInFilm(BaseModel):
    """An API model to represent person information within FilmFull class.

    """
    id: str
    name: str | None


class FilmFull(FilmShort, BaseModel):
    """An API model to represent detailed information on a film.

    """
    description: str | None
    genres: list[GenreInFilm] | None = Field(default=[])
    actors: list[PersonInFilm] | None = Field(default=[])
    writers: list[PersonInFilm] | None = Field(default=[])
    directors: list[PersonInFilm] | None = Field(default=[])


class Genre(BaseModel):
    id: str
    name: str


class GenreList(BaseModel):
    results: list[Genre]


class FilmPersonRoles(BaseModel):
    id: str
    roles: list[str]


class PersonShortFilmInfo(BaseModel):
    id: str
    title: str
    imdb_rating: float


class PersonShortFilmInfoList(BaseModel):
    total: int
    results: list[PersonShortFilmInfo]


class Person(BaseModel):
    id: str
    full_name: str
    films: list[FilmPersonRoles]


class PersonList(BaseModel):
    total: int
    page: int
    size: int
    prev: str | None
    next: str | None
    results: list[Person]
