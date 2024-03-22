import datetime

import pydantic


class JWToken(pydantic.BaseModel):
    exp: datetime.datetime
    sub: str


class JWTUser(pydantic.BaseModel):
    username: str

class JWTBookshelfWSUser(pydantic.BaseModel):
    id: str
    bookshelf_id: str