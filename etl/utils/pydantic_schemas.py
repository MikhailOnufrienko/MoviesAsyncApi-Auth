import uuid

from pydantic import BaseModel


class PersonInfo(BaseModel):
    id: uuid.UUID
    full_name: str
