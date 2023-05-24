from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from utils.paginator_page_size_calc import get_page_size

from api.v1.schemes import (Person, PersonList, PersonShortFilmInfo,
                            PersonShortFilmInfoList)
from services.person import PersonService, get_person_service
from utils.constants import PERSON_NOT_FOUND

router = APIRouter()


@router.get('/search', response_model=PersonList, summary='Person list')
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

    - **total**: total number of all persons found
    - **page**: current page number
    - **size**: size of page
    - **prev**: link to previous page
    - **next**: link to next page
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
        size = None
    else:
        prev = (
            f'/persons/search?query={query}&page_number={page_number-1}'
            if page_number > 1 else None
        )
        next = (
            f'/persons/search?query={query}&page_number={page_number+1}'
            if (page_number - 1) * page_size + len(objects) < total else None
        )
        size = get_page_size(page_number, total, page_size, next)

    return PersonList(
        total=total,
        page=page_number,
        size=size,
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

    - **total**: total number of all films related to the person selected
    - **results**: list of films
    """

    total, films = await person_service.get_person_films_list(person_id)

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
