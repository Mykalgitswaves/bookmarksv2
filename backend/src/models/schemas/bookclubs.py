from datetime import datetime, timezone
from neo4j.time import DateTime as Neo4jDateTime
from pydantic import (
    BaseModel, 
    EmailStr, 
    validator, 
)
from typing import Mapping, List, Any

class BaseBookClub(BaseModel):
    book_club_id: str
    book_club_name: str
    currently_reading_book: Any | None = None
    pace: int | None
    
    errors = {
        'unauthorized': {
            'status_code': 500,
            'detail': "Unauthorized, you do not have permission to make this request"
        },
    }

    def get_pace_offset(record):
        if (record.get("expected_finish_date") 
            and record.get("total_chapters") is not None
            and record.get("current_chapter") is not None
        ):
            started_date = record.get("started_date")
            expected_finish_date = record.get("expected_finish_date")
            total_chapters = record.get("total_chapters")
            current_chapter = record.get("current_chapter")

            if isinstance(started_date, Neo4jDateTime):
                started_date = started_date.to_native()

            if isinstance(expected_finish_date, Neo4jDateTime):
                expected_finish_date = expected_finish_date.to_native()

            current_date = datetime.now(timezone.utc)

            # Calculate total reading duration in days
            total_days = (expected_finish_date - started_date).days
            # Calculate elapsed days since the start
            elapsed_days = (current_date - started_date).days

            # Calculate expected chapters by the current date
            expected_chapters = (elapsed_days / max(total_days,1)) * max(total_chapters,1)

            # Calculate offset from the expected chapter
            pace_offset = current_chapter - round(expected_chapters)
        else:
            pace_offset = None
        
        return pace_offset
         

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
    user_ids: List[str] | None = None
    emails: List[EmailStr] | None = None


class BookClubList(BaseModel):
    user_id: str
    limit: int | None


class BookClubPreview(BaseBookClub):
    pass


class MinimalBookClub(BaseBookClub):
    # Making this extend bookclub preview for when we have more data to gather
    pass

class BookClubCurrentlyReading(BaseModel):
    book_id: str
    title: str
    small_img_url: str

class BookClubInvitePreview(BaseModel):
    invite_id: str
    book_club_id: str
    book_club_name: str
    book_club_owner_name: str
    num_mutual_friends: int
    datetime_invited: datetime

    @validator('datetime_invited', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v



# We don't need any info ab the club they were invited to 
# in this since it is only viewable from a particular clubs settings.
class BookClubInviteAdminPreview(BaseModel):
    invite_id: str
    invited_user: Mapping[str, str]
    datetime_invited: datetime
    
    @validator('datetime_invited', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v

class BookClubInviteResponse(BaseModel):
    invite_id: str
    user_id: str

class BookClubPaces(BaseModel):
    expected_pace: int
    user_pace: int
    club_pace: int
    total_chapters: int

class StartCurrentlyReading(BaseModel):
    expected_finish_date: datetime
    book: dict
    user_id: str
    id: str

class UpdatePost(BaseModel):
    user: dict
    chapter: int
    response: str | None
    headline: str | None
    quote: str | None
    id: str