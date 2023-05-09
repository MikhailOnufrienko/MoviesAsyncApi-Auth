from http import HTTPStatus
from typing import Annotated
from uuid import UUID


from fastapi import APIRouter, Depends, HTTPException, Query, Path

from src.services.film import FilmService, get_film_service
from src.api.v1.schemes import FilmFull, FilmList
from src.utils.constants import FILM_NOT_FOUND

router = APIRouter()


@router.get(
    '/',
    response_model=FilmList,
    summary='List of films'
)
async def filmlist(
    page_number: Annotated[
        int, Query(description='Pagination page number', ge=1)
    ] = 1,
    page_size: Annotated[
        int, Query(description='Pagination page size', ge=1)
    ] = 20,
    genre: Annotated[UUID, Query(description='Search by genre id')] = None,
    film_service: FilmService = Depends(get_film_service)
) -> FilmList:
    """
    Return list of films with parameters:
    
    - **total**: total number of all films in database
    - **page**: current page number
    - **size**: size of page
    - **prev**: link to previous page
    - **next**: link to next page
    - **results**: list of film information
    """

    total, filmlist = await film_service.get_films(
        page=page_number, size=page_size, genre=genre
    )

    if total == 0:
        prev = None
        next = None
        size = None
    else:
        prev = f'/films?page={page_number-1}' if page_number > 1 else None
        next = (
            f'/films?page={page_number+1}'
            if (page_number - 1) * page_size + len(filmlist) < total
            else None
        )
        size = get_page_size(page_number, total, page_size, next)

    return FilmList(
        total=total,
        page=page_number,
        size=size,
        prev=prev,
        next=next,
        results=[{
            "id": film.id,
            "title": film.title,
            "imdb_rating": film.imdb_rating
        } for film in filmlist] if total else []
    )


@router.get('/search', response_model=FilmList, summary='Film search')
async def film_search(
        query: Annotated[str, Query(description='Film search query')],
        page_number: Annotated[
            int, Query(description='Pagination page number', ge=1)
        ] = 1,
        page_size: Annotated[
            int, Query(description='Pagination page size', ge=1)
        ] = 20,
        film_service: FilmService = Depends(get_film_service)
) -> FilmList:
    """
    Return list of films by query:
    
    - **total**: total number of all films in database
    - **page**: current page number
    - **size**: size of page
    - **prev**: link to previous page
    - **next**: link to next page
    - **results**: list of film information
    """

    total, filmlist = await film_service.search_films(
        query=query, page=page_number, size=page_size
    )

    if total == 0:
        prev = None
        next = None
        size = None
    else:
        prev = (
            f'/films/search?query={query}&page={page_number-1}'
            if page_number > 1 else None
        )
        next = (
            f'/films/search?query={query}&page={page_number+1}'
            if (page_number - 1) * page_size + len(filmlist) < total else None
        )

        size = get_page_size(page_number, total, page_size, next)

    return FilmList(
        total=total,
        page=page_number,
        size=size,
        prev=prev,
        next=next,
        results=[{
            "id": film.id,
            "title": film.title,
            "imdb_rating": film.imdb_rating
        } for film in filmlist] if total else []
    )


@router.get('/{film_id}', response_model=FilmFull, summary='Film detail')
async def film_details(
    film_id: str,
    film_service: FilmService = Depends(get_film_service)
) -> FilmFull:
    """
    Return film information:

    - **description**: film description
    - **genres**: list of film genres
    - **actors**: list of film actors
    - **writers**: list of film writers
    - **directors**: film directors
    """

    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=FILM_NOT_FOUND
        )
    return FilmFull(
        id=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=film.genre,
        actors=film.actors,
        writers=film.writers,
        directors=film.director,
    )


def get_page_size(
    page: int,
    total: int,
    size_default: int,
    next: str | None
) -> int:

    if total >= size_default:
        if next:
            return size_default
        else:
            return total - size_default * (page - 1)
    return total
