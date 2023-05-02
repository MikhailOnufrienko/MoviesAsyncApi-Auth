from http import HTTPStatus


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.person import PersonService, get_person_service


router = APIRouter()


class PersonShortFilm(BaseModel):
    uuid: str
    roles: list


class Person(BaseModel):
    id: str
    full_name: str
    films: list[PersonShortFilm]


@router.get('/search')
async def person_list_search(
    person_service: PersonService = Depends(get_person_service),
    page: int = 1,
    page_size: int = 10,
    query: str | None = None
) -> list:
    """API Endpoint for a list of persons and their roles in films."""

    objects = await person_service.get_object_list(page, page_size, query)
    data = []

    for item in objects:
        person, films = item
        data.append(
            Person(
                id=person.id,
                full_name=person.full_name,
                films=films
            )
        )

    return data


@router.get('/{person_id}', response_model=Person)
async def person_detail(
    person_id: str,
    person_service: PersonService = Depends(get_person_service)
) -> Person | HTTPException:
    """API Endpoint to retrieve information about a person by his id."""

    person, movies = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='person not found'
        )

    return Person(id=person.id, full_name=person.full_name, films=movies)


@router.get('/{person_id}/film')
async def person_detail_films(
    person_id: str,
    person_service: PersonService = Depends(get_person_service)
) -> list:
    """
    API Endpoint to get information about films
    in which the person was involved.
    """

    movies = await person_service.get_films_by_person(person_id)

    return movies
