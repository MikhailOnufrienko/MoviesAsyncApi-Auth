from datetime import datetime
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class UUIDMixin(BaseModel):
    id: UUID


class TimestampedMixin(BaseModel):
    pass


class ORJSONMixin(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
