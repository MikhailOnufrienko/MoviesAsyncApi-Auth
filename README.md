# API и ETL сервис для онлайн-кинотеатра MoviesAsyncApi

Проект позволяет запускать приложения в docker-контейнерах. Поднимаются сервисы:
Api, ETL, PostgreSQL, ElasticSearch, Redis.

<hr>

### Заполнить файл "```.env```" в корневой директории "```etl```" по шаблону из файла .env.example:
```sh
PROJECT_NAME=<PROJECT NAME>

REDIS_HOST=<REDIS HOST>
REDIS_PORT=<REDIS PORT>

ELASTIC_SCHEME=<SCHEME FOR ES>
ELASTIC_HOST=<ES HOST>
ELASTIC_PORT=<ES PORT>

LOGLEVEL=<LOGGING LEVEL>
POSTGRES_DB=<DATABASE_NAME>
POSTGRES_USER=<USER USERNAME>
POSTGRES_PASSWORD=<USER PASSWORD>
DB_HOST=<POSTGRES HOST>
DB_PORT=<POSTGRES PORT>
```

<hr>

## Запуск проекта в Docker контейнерах:

#### Клонировать проект
```sh
https://github.com/AltyOfficial/MoviesAsyncApi.git
```

#### Файл конфигурации docker-compose находится в корневой директории, выполнить команду для запуска контейнеров:
```sh
docker-compose up -d --build
```
- Команда ```-d``` нужна для фоновой работы контейнера

#### После выполнения всех шагов, будет работать постоянный и устойчивый ETL-процесс, а так же функционирующее API по адресу ```http://localhost/```. Документацию к эндпоинтам API можно посмотреть по адресу ```http://localhost/api/openapi```