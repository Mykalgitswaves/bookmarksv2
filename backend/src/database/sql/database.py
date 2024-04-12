from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.config.config import settings

class AsyncMySQLDatabase:
    def __init__(self):
        self.url = URL.create(
            drivername="mysql+asyncmy",
            username=settings.MYSQL_USERNAME,
            password=settings.MYSQL_PASSWORD,
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            database=settings.MYSQL_DATABASE
        )

        self.async_engine = create_async_engine(self.url,
                                                echo=settings.MYSQL_ECHO)
        self.pool = async_sessionmaker(self.async_engine,
                                       class_=AsyncSession,
                                       expire_on_commit=False)

async_mysql_database: AsyncMySQLDatabase = AsyncMySQLDatabase()