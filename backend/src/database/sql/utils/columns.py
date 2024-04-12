from sqlalchemy import VARCHAR
from typing_extensions import Annotated
from sqlalchemy.orm import mapped_column

str_pk = Annotated[
    str,
    mapped_column(
        VARCHAR(255),
        primary_key=True
    )
]


str_255 = Annotated[
    str,
    mapped_column(
        VARCHAR(255)
    )
]