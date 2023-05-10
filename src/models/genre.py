from src.models.mixins import UUIDMixin, ORJSONMixin


class Genre(ORJSONMixin, UUIDMixin):
    """A model to retrieve information on a genre.

    """
    name: str
