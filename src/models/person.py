from models.film import FilmPersonRoles
from models.mixins import UUIDMixin, ORJSONMixin


class PersonShort(ORJSONMixin, UUIDMixin):
    """A model to retrieve information on a person.

    """
    full_name: str


class PersonFull(ORJSONMixin, UUIDMixin):
    """A model to retrieve information on a person and his roles in films.

    """
    full_name: str
    films: list[FilmPersonRoles]
