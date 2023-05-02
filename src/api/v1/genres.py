from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from elasticsearch import Elasticsearch
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service


router = APIRouter()


class Genre(BaseModel):
    uuid: str
    name: str


@router.get('/{genre_id}', response_model=Genre)
async def genre_detail(
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service)
) -> Genre | HTTPException:
    """pass"""
    
    genre = await genre_service.get_by_id(genre_id)

    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genre not found'
        )

    return Genre(id=genre.id, title=genre.title)


@router.get('/')
async def genre_list(
    genre_service: GenreService = Depends(get_genre_service)
) -> list[Genre | None]:
    """pass"""

    genres = await genre_service.get_list()

    return genres
