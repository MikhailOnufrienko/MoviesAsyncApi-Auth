from http import HTTPStatus


from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter, Depends
from elasticsearch import Elasticsearch
from pydantic import BaseModel

from services.person import PersonService, get_person_service


router = APIRouter()


class Person(BaseModel):
    id: str
    full_name: str


@router.get('/{person_id}', response_model=Person)
async def person_detail(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Person:
    """pass."""

    person = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=404, detail='person not found'
        )
    
    return Person(id=person.id, full_name=person.full_name)
