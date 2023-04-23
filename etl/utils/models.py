import uuid

from pydantic import BaseModel


class FilmworkInfo(BaseModel):
    id: uuid.UUID
    full_name: str
