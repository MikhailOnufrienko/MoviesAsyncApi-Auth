from fastapi import APIRouter, Depends

from pydantic import BaseModel


router = APIRouter()


class Genre(BaseModel):
    id: str
    title: str


@router.get('/{genre_id}', response_model=Genre)
async def genre_detail(genre_id: str) -> Genre:
    return Genre(id=genre_id, title='title')
