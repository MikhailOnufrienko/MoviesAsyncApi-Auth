from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src.services.genre import GenreService, get_genre_service
from src.api.v1.schemes import Genre, GenreList


router = APIRouter()


@router.get('/', response_model=GenreList)
async def genre_list(
    genre_service: GenreService = Depends(get_genre_service),
    page_number: Annotated[
        int, Query(description='Pagination page number', ge=1)
    ] = 1,
    page_size: Annotated[
        int, Query(description='Pagination page size')
    ] = 10
) -> GenreList:
    """API Endpoint for genre list information."""

    genres = list(await genre_service.get_genre_list(page_number, page_size))

    return GenreList(
        results=[
            Genre(
                id=genre.id,
                name=genre.name,
            ) for genre in genres]
    )


@router.get('/{genre_id}', response_model=Genre)
async def genre_detail(
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service)
) -> Genre | HTTPException:
    """API Endpoint for genre information."""

    genre = await genre_service.get_by_id(genre_id)

    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genre not found'
        )

    return Genre(id=genre.id, name=genre.name)
