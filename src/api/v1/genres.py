from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from elasticsearch import Elasticsearch
from pydantic import BaseModel

from services.genre import GenreServise, get_genre_service


router = APIRouter()


class Genre(BaseModel):
    id: str
    title: str


@router.get('/{genre_id}', response_model=Genre)
async def genre_detail(genre_id: str, genre_service: GenreServise = Depends(get_genre_service)) -> Genre:
    
    genre = await genre_service.get_by_id(genre_id)

    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genre not found'
        )

    return Genre(id=genre.id, title=genre.title)
