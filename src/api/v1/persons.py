from http import HTTPStatus
from typing import Annotated


from fastapi import APIRouter, Depends, HTTPException, Query

from services.person import PersonService, get_person_service
from src.api.v1.schemes import (FilmPersonRoles, Person, PersonList,
                                PersonShortFilmInfo, PersonShortFilmInfoList)


router = APIRouter()


@router.get('/search')
async def person_list_search(
    person_service: PersonService = Depends(get_person_service),
    page: Annotated[
        int, Query(description='Pagination page', ge=1)
    ] = 1,
    page_size: Annotated[
        int, Query(description='Pagination page size', ge=1)
    ] = 10,
    query: str | None = None
) -> list[Person]:
    """API Endpoint for a list of persons and their roles in films."""

    objects = await person_service.get_person_list(page, page_size, query)

    return PersonList(
        results=[
            Person(
                id=person.id,
                full_name=person.full_name,
                films=person.films
            ) for person in objects
        ]
    )


@router.get('/{person_id}', response_model=Person)
async def person_detail(
    person_id: str,
    person_service: PersonService = Depends(get_person_service)
) -> Person | HTTPException:
    """API Endpoint to retrieve information about a person by his id."""

    person = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='person not found'
        )

    return Person(
        id=person.id,
        full_name=person.full_name,
        films=person.films,
    )


@router.get('/{person_id}/film')
async def person_films_detail(
    person_id: str,
    person_service: PersonService = Depends(get_person_service)
) -> list[FilmPersonRoles]:
    """
    API Endpoint to get information about films
    in which the person was involved.
    """

    films = await person_service.get_person_films_list(person_id)

    return PersonShortFilmInfoList(
        results=[
            PersonShortFilmInfo(
                id=film.id,
                title=film.title,
                imdb_rating=film.imdb_rating,
            ) for film in films
        ]
    )
