from auth.src.core.config import app_settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker


DATABASE_DSN = 'postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}'.format(
    user=app_settings.DB_USER,
    password=app_settings.DB_PASSWORD,
    host=app_settings.DB_HOST,
    port=app_settings.DB_PORT,
    name=app_settings.DB_NAME
)

# Создаём движок
# Настройки подключения к БД передаём из переменных окружения, которые заранее загружены в файл настроек
engine = create_async_engine(DATABASE_DSN, echo=True, future=True)
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# Функция понадобится при внедрении зависимостей
# Dependency
async def get_postgres_session() -> AsyncSession:
    async with async_session.begin() as session:
        yield session
