from http import HTTPStatus


from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter, Depends
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
        raise HTTPException(status_code=404, detail='genre not found')

    return Genre(id=genre.id, title=genre.title)


if __name__ == '__main__':
    es = Elasticsearch(hosts='http://localhost:9200/')
    doc = es.get(index='person_index', id='42a001e7-6c61-4620-b022-27cd534fbaaf')
    print(doc['_source'])
    # index_name = 'person_index'
    # query = {"query": {"match_all": {}}}
    # response = es.search(index=index_name, query={"match_all": {}})
    # hits = response["hits"]["hits"]
    # for hit in hits:
    #     print(hit["_source"])