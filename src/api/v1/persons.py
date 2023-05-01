from http import HTTPStatus


from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter, Depends
from elasticsearch import Elasticsearch
from pydantic import BaseModel

from services.person import PersonService, get_person_service
import json


router = APIRouter()


class PersonShortFilm(BaseModel):
    uuid: str
    roles: list


class Person(BaseModel):
    id: str
    full_name: str
    films: list[PersonShortFilm]


# @router.get('/')
# async def person_list(person_service: PersonService = Depends(get_person_service), page: int = 1, page_size: int = 10, query: str | None = None):

#     # objects = [Person(id='1', full_name='Name One'), Person(id='2', full_name='Name Two')]

#     # return [dict(p) for p in objects]

#     objects = await person_service.get_object_list(page, page_size, query)

#     return [dict(p) for p in objects]

#     # persons = await person_service.get_list()

#     # objects = ['James', 'Sandor']
#     # return json.dumps(objects)

#     # return persons


@router.get('/search')
async def person_list_search(person_service: PersonService = Depends(get_person_service), page: int = 1, page_size: int = 10, query: str | None = None):
    objects = await person_service.get_object_list(page, page_size, query)

    # return [dict(p) for p in objects]

    data = []

    for item in objects:
        person, films = item[0], item[1]
        data.append(Person(id=person.id, full_name=person.full_name, films=films))

    return data


@router.get('/{person_id}', response_model=Person)
async def person_detail(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Person:
    """pass."""

    person, movies = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=404, detail='person not found'
        )
    
    return Person(id=person.id, full_name=person.full_name, films=movies)
