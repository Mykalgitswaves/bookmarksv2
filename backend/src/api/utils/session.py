from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.sql.database import async_mysql_database  # Import your database setup

async def get_session():
    async with async_mysql_database.pool() as session:
        try:
            yield session
        except Exception as e:
            print(e)
        finally:
            await session.close()