import orjson

from models.mixins import UUIDMixin, ORJSONMixin


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Genre(ORJSONMixin, UUIDMixin):
    """A model to retrieve information on a genre.

    """
    name: str
