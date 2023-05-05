from elasticsearch import AsyncElasticsearch

es: AsyncElasticsearch | None = 'http://localhost:9200/'

# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    return es
