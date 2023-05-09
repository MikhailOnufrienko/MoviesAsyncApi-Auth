from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.v1.schemes import Genre, GenreList
from src.services.genre import GenreService, get_genre_service
from src.utils.constants import GENRE_NOT_FOUND

router = APIRouter()


@router.get('/', response_model=GenreList, summary='Genre list')
async def genre_list(
    genre_service: GenreService = Depends(get_genre_service),
    page_number: Annotated[
        int, Query(description='Pagination page number', ge=1)
    ] = 1,
    page_size: Annotated[
        int, Query(description='Pagination page size')
    ] = 10
) -> GenreList:
    """
    Return list of genres with parameters:

    - **results**: Genre object list
    """

    genres = list(await genre_service.get_genre_list(page_number, page_size))

    return GenreList(
        results=[
            Genre(
                id=genre.id,
                name=genre.name,
            ) for genre in genres]
    )


@router.get('/{genre_id: str}', response_model=Genre, summary='Genre detail')
async def genre_detail(
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service)
) -> Genre | HTTPException:
    """
    Return genre information:

    - **id**: genre id
    - **name**: genre name
    """

    genre = await genre_service.get_by_id(genre_id)

    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=GENRE_NOT_FOUND
        )

    return Genre(id=genre.id, name=genre.name)
