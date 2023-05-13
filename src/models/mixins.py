from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class UUIDMixin(BaseModel):
    id: str


class ORJSONMixin(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
