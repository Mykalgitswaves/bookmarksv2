from pydantic import BaseModel

class SetupUserFullName(BaseModel):
    full_name: str

class SetupUserGenres(BaseModel):
    genres: list[str]

class SetupUserAuthors(BaseModel):
    authors: list[str]