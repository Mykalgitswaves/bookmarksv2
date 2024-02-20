from pydantic import BaseModel

class AuthorName(BaseModel):
    name:str

class AuthorId(BaseModel):
    id:str

class Author(BaseModel):
    name:str
    id:str
    books:list = []