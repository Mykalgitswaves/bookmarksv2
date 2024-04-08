from datetime import datetime
from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declared_attr

class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

class TimestampMixin:
    create_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )

    update_at: Mapped[datetime] =  mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )