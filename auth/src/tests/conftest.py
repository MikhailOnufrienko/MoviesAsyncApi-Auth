import logging
import time
from typing import AsyncGenerator
from sqlalchemy import select, text

import asyncio
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.pool import NullPool
from werkzeug.security import generate_password_hash

from auth.src.models.entity import User, metadata_obj
from auth.src.db.postgres import get_postgres_session
from auth.main import app
from auth.src.tests.functional.config import settings


logger = logging.getLogger(name='__name__')


DATABASE_DSN: str = 'postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}'.format(
    user=settings.TEST_DB_USER,
    password=settings.TEST_DB_PASSWORD,
    host=settings.TEST_DB_HOST,
    port=settings.TEST_DB_PORT,
    name=settings.TEST_DB_NAME
)

async_engine: AsyncEngine = create_async_engine(DATABASE_DSN, poolclass=NullPool)

async_session: AsyncSession = async_sessionmaker(async_engine, expire_on_commit=False)

metadata_obj.bind = async_engine

client = TestClient(app)


async def override_get_postgres_session() -> AsyncSession:
    async with async_session() as session:
        yield session 


app.dependency_overrides[get_postgres_session] = override_get_postgres_session


@pytest.fixture(autouse=True, scope='session')
async def create_schema():
    async with async_session() as session:
        query = text('CREATE SCHEMA IF NOT EXISTS auth;')
        await session.execute(query)
        await session.commit()


@pytest.fixture(scope='session')
async def prepare_db(create_schema):
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata_obj.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata_obj.drop_all)


@pytest.fixture(scope='session')
async def create_user(prepare_db):
    async with async_session() as session:
        existing_wizard = select(User.login).filter(User.login == "wizard")
        result = await session.execute(existing_wizard)
        if not result.scalar_one_or_none():
            hashed_password = generate_password_hash('cogitoergosum')
            wizard_user = User(login='wizard', hashed_password=hashed_password, email='wizard@ratio.org', first_name='David', last_name='Copperfield')
            session.add(wizard_user)
            await session.commit()


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
