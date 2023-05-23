from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.schemes import (Person, PersonList, PersonShortFilmInfo,
                            PersonShortFilmInfoList)
from services.person import PersonService, get_person_service
from utils.constants import PERSON_NOT_FOUND

router = APIRouter()


@router.get('/search', response_model=PersonList, summary='Person lsit')
async def person_list_search(
    person_service: PersonService = Depends(get_person_service),
    page_number: Annotated[
        int, Query(description='Pagination page number', ge=1)
    ] = 1,
    page_size: Annotated[
        int, Query(description='Pagination page size', ge=1)
    ] = 10,
    query: str | None = None
) -> PersonList:
    """
    Return person list by query:

    - **results**: list of persons
    """

    total, objects = await person_service.get_person_list(
        page_number,
        page_size,
        query
    )

    if total == 0:
        prev = None
        next = None
    else:
        prev = (
            f'/persons/search?&page_number={page_number - 1}'
            f'&page_size={page_size}'
        )
        prev += f'query={query}' if query else ''

        if page_number <= 1:
            prev = None

        next = (
            f'/persons/search?&page_number={page_number + 1}'
            f'&page_size={page_size}'
        )
        next += f'query={query}' if query else ''

        if (page_number - 1) * page_size + len(objects) >= total:
            next = None

    obj = PersonList(
        total=total,
        page=page_number,
        size=len(objects),
        prev=prev,
        next=next,
        results=[
            Person(
                id=person.id,
                full_name=person.full_name,
                films=person.films
            ) for person in objects
        ]
    )

    return obj


@router.get('/{person_id}', response_model=Person, summary='Person detail')
async def person_detail(
    person_id: str,
    person_service: PersonService = Depends(get_person_service)
) -> Person | HTTPException:
    """
    Return person information:

    - **id**: genre id
    - **full_name**: Person's full name
    - **films**: list of films and the person's roles
    """

    person = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND
        )

    return Person(
        id=person.id,
        full_name=person.full_name,
        films=person.films,
    )


@router.get(
    '/{person_id}/film',
    response_model=PersonShortFilmInfoList,
    summary='List of person\'s films'
)
async def person_films_detail(
    person_id: str,
    person_service: PersonService = Depends(get_person_service)
) -> PersonShortFilmInfoList:
    """
    Return list of films in which the person participated:

    - **results**: list of films
    """

    total, films = await person_service.get_person_films_list(person_id)

    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND
        )

    return PersonShortFilmInfoList(
        total=total,
        results=[
            PersonShortFilmInfo(
                id=film.id,
                title=film.title,
                imdb_rating=film.imdb_rating,
            ) for film in films
        ]
    )
