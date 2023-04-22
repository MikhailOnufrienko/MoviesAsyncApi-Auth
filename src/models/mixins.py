from datetime import datetime

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class UUIDMixin(BaseModel):
    id: UUID


class TimestampedMixin(BaseModel):
    created: datetime
    modified: datetime


class ORJSONMixin(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
