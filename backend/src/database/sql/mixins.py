from datetime import datetime
from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declared_attr

def camel_to_snake(name: str) -> str:
    """
    Converts a string from CamelCase to snake_case.

    Parameters:
    name (str): The CamelCase string to convert.

    Returns:
    str: The converted snake_case string.
    """
    # Start with the first character in lowercase.
    snake_case = [name[0].lower()]
    
    # Iterate over the rest of the characters.
    for char in name[1:]:
        # If the character is uppercase, add an underscore and then its lowercase.
        if char.isupper():
            snake_case.append('_' + char.lower())
        else:
            snake_case.append(char)
    
    # Join the list into a string and return.
    return ''.join(snake_case)


class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__) + "s"

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