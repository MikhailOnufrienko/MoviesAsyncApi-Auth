from typing import Any

from pydantic import BaseModel


class HTTPResponse(BaseModel):
    body: Any
    status: int


class Genre(BaseModel):
    id: str
    name: str
