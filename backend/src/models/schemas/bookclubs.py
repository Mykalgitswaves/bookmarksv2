from pydantic import BaseModel
from typing import Mapping

class BookClubCreate(BaseModel):
    user_id: str
    name: str
    description: str
    book_club_pace: dict | None = None