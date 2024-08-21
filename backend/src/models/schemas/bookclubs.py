from pydantic import BaseModel, EmailStr
from typing import Mapping, List

class BookClubCreate(BaseModel):
    user_id: str
    name: str
    description: str
    book_club_pace: dict | None = None

class BookClubInviteSearch(BaseModel):
    book_club_id: str
    param: str
    limit: int = 10

class BookClubInvite(BaseModel):
    book_club_id: str
    user_id: str
    user_ids: List[str]
    emails: List[EmailStr]

