from mixins import ORJSONMixin, TimestampedMixin, UUIDMixin


class Film(UUIDMixin, TimestampedMixin, ORJSONMixin):
    title: str
    description: str


class Genre(UUIDMixin, TimestampedMixin, ORJSONMixin):
    title: str
    description: str


class Person(UUIDMixin, TimestampedMixin, ORJSONMixin):
    full_name: str
