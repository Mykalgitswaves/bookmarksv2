from sqlalchemy.ext.asyncio import AsyncSession

class BaseCRUDRepositoryMySQL:
    def __init__(self, session: AsyncSession):
        self.session = session