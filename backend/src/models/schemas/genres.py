from pydantic import BaseModel

class GenreName(BaseModel):
    name:str

class GenreId(BaseModel):
    id:str

class Genre(BaseModel):
    name:str
    id:str