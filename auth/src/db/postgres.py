from auth.src.core.config import app_settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker


DATABASE_DSN: str = 'postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}'.format(
    user=app_settings.DB_USER,
    password=app_settings.DB_PASSWORD,
    host=app_settings.DB_HOST,
    port=app_settings.DB_PORT,
    name=app_settings.DB_NAME
)

async_engine: AsyncEngine = create_async_engine(DATABASE_DSN, echo=True, future=True)

async_session: AsyncSession = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_postgres_session() -> AsyncSession:
    async with async_session() as session:
        yield session 
