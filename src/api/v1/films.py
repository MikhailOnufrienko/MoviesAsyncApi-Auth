from http import HTTPStatus
from uuid import UUID


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from services.film import FilmService, get_film_service

# Объект router, в котором регистрируем обработчики
router = APIRouter()

# FastAPI в качестве моделей использует библиотеку pydantic
# https://pydantic-docs.helpmanual.io
# У неё есть встроенные механизмы валидации, сериализации и десериализации
# Также она основана на дата-классах

# Модель ответа API
class FilmShort(BaseModel):
    id: UUID
    title: str
    imdb_rating: float


class FilmList(BaseModel):
    total: int
    page: int
    size: int
    results: list[FilmShort]

class Genre(BaseModel):
    id: UUID
    name: str

class Person(BaseModel):
    id: UUID
    name: str | None


class FilmFull(FilmShort, BaseModel):
    description: str | None
    genres: list[Genre] | None = Field(default=[])
    actors: list[Person] | None = Field(default=[])
    writers: list[Person] | None = Field(default=[])
    directors: list[Person] | None = Field(default=[])


@router.get('/', response_model=FilmList)
async def filmlist(
    page: int = 1,
    size: int = 50,
    film_service: FilmService = Depends(get_film_service)
) -> FilmList:
    total, filmlist = await film_service.get_films(page=page, size=size)
    return FilmList(
        total=total,
        page=page,
        size=size,
        results=[{
            "id": film.id,
            "title": film.title,
            "imdb_rating": film.imdb_rating}for film in filmlist]
        )


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}', response_model=FilmFull)
async def film_details(
    film_id: str,
    film_service: FilmService = Depends(get_film_service)
) -> FilmFull:
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum  
                # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description 
        # Которое отсутствует в модели ответа API. 
        # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
        # вы бы предоставляли клиентам данные, которые им не нужны 
        # и, возможно, данные, которые опасно возвращать
    return FilmFull(
        id=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=film.genre,
        actors=film.actors,
        writers=film.writers,
        directors=film.director
        )
 
