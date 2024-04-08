from sqlalchemy import VARCHAR, ForeignKey
from typing import Optional
from typing_extensions import Annotated
from sqlalchemy.orm import Mapped, mapped_column

from src.database.sql.base import Base
from src.database.sql.mixins import TableNameMixin, TimestampMixin
from src.database.sql.utils.columns import str_pk, str_255

user_fk = Annotated[
    str,
    mapped_column(
        VARCHAR(255),
        ForeignKey("users.user_id", ondelete="SET NULL")
    )
]

class User(Base, TimestampMixin, TableNameMixin):
    user_id: Mapped[str_pk]
    full_name: Mapped[str_255]
    username: Mapped[str_255]
    email: Mapped[str_255]
    referrer_id: Mapped[Optional[user_fk]]

class UserBook(Base, TimestampMixin, TableNameMixin):
    pk: Mapped[str_pk]
    user_id: Mapped[str] = mapped_column(
        VARCHAR(255),
        ForeignKey("users.user_id", ondelete="CASCADE")
    )
    book_id: Mapped[str] = mapped_column(
        VARCHAR(255),
        ForeignKey("books.book_id", ondelete="CASCADE")
    )
    status: Mapped[str_255]