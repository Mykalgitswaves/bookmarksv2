from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column

from src.database.sql.base import Base
from src.database.sql.mixins import TableNameMixin, TimestampMixin
from src.database.sql.utils.columns import str_pk, str_255

class BookTest(Base, TimestampMixin, TableNameMixin):
    book_id: Mapped[str_pk]
    title: Mapped[str_255]
    description: Mapped[Optional[str_255]]