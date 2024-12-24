from pydantic import BaseModel
from typing import Union, Optional
from src.models.schemas.social import FriendUser

class SearchSchema(BaseModel):
    param: str

class SearchResultUser(FriendUser):
    pass

class SearchResultBookClub(BaseModel):
    current_book: dict | None
    name: str
    number_of_members: int
    id: str