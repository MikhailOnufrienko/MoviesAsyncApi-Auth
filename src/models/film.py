from models.mixins import UUIDMixin, ORJSONMixin


class FilmPersonRoles(ORJSONMixin, UUIDMixin):
    """A model to retrieve information on films and person's roles in films.

    """
    roles: list[str]


class PersonShortFilmInfo(ORJSONMixin, UUIDMixin):
    """A model to retrieve short information on a person's films.

    """
    title: str
    imdb_rating: float
