from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from api.v1.films import get_page_size

from api.v1.schemes import Genre, GenreList
from services.genre import GenreService, get_genre_service
from utils.constants import GENRE_NOT_FOUND

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

    total, genrelist = await genre_service.get_genre_list(
        page=page_number, page_size=page_size
    )

    if total == 0:
        prev = None
        next = None
        size = None
    else:
        prev = (
            f'/genres?page_number={page_number-1}' if page_number > 1 else None
        )
        next = (
            f'/genres?page_number={page_number+1}'
            if (page_number - 1) * page_size + len(genrelist) < total else None
        )
        size = get_page_size(page_number, total, page_size, next)

    return GenreList(
        total=total,
        page=page_number,
        size=size,
        prev=prev,
        next=next,
        results=[{
            "id": genre.id,
            "name": genre.name
        } for genre in genrelist] if total else []
    )

#    genres = list(await genre_service.get_genre_list(page_number, page_size))

#    return GenreList(
#        results=[
#            Genre(
#                id=genre.id,
#                name=genre.name,
#            ) for genre in genres]
#    )


@router.get('/{genre_id}', response_model=Genre, summary='Genre detail')
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
