from pydantic import BaseModel, EmailStr
from typing import Mapping, List, Any

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

class BookClubList(BaseModel):
    user_id: str
    limit: int | None

class BookClubPreview(BaseModel):
    book_club_id: str
    book_club_name: str
    pace: int | None
    currently_reading_book: Any | None = None

class BookClubCurrentlyReading(BaseModel):
    book_id: str
    title: str
    small_img_url: str