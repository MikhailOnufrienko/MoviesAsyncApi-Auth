from http import HTTPStatus


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.person import PersonService, get_person_service


router = APIRouter()


class FilmPersonRoles(BaseModel):
    id: str
    roles: list[str]


class PersonShortFilmInfo(BaseModel):
    id: str
    title: str
    imdb_rating: float


class PersonShortFilmInfoList(BaseModel):
    results: list[PersonShortFilmInfo]


class Person(BaseModel):
    id: str
    full_name: str
    films: list[FilmPersonRoles]


class PersonList(BaseModel):
    results: list[Person]


@router.get('/search')
async def person_list_search(
    person_service: PersonService = Depends(get_person_service),
    page: int = 1,
    page_size: int = 10,
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
