from sqlalchemy import select, delete, insert

from src.database.sql.crud.base import BaseCRUDRepositoryMySQL
from src.database.sql.models.users import UserTest


class UserRepository(BaseCRUDRepositoryMySQL):
    async def create_user(self, user: UserTest):
        query = insert(UserTest).values(
            user_id=user.user_id,
            full_name=user.full_name,
            username=user.username,
            email=user.email,
            referrer_id=user.referrer_id
        )
        await self.session.execute(query)
        await self.session.commit()
        return user
    
    async def get_user(self, user_id: str):
        query = select(UserTest).filter(UserTest.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def delete_user(self, user_id: str):
        query = delete(UserTest).filter(UserTest.user_id == user_id)
        await self.session.execute(query)
        await self.session.commit()
        return user_id

