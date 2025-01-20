from datetime import datetime, timezone
from neo4j.time import DateTime as Neo4jDateTime
from pydantic import (
    BaseModel, 
    EmailStr, 
    validator,
    Field,
    conint
)
from typing import Mapping, List, Any, Literal, Optional

from src.models.schemas.posts import Post
from src.config.config import settings

class BaseBookClub(BaseModel):
    book_club_id: str
    book_club_name: str
    currently_reading_book: Any | None = None
    pace: int | None
    
    # errors = {
    #     'unauthorized': {
    #         'status_code': 500,
    #         'detail': "Unauthorized, you do not have permission to make this request"
    #     },
    # }

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
            # Cannot be more than the total number of chapters in the book
            expected_chapters = min((elapsed_days / max(total_days,1)) * max(total_chapters,1),total_chapters)

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
    book_club_description: str
    # Making this extend bookclub preview for when we have more data to gather
    pass

class BookClubCurrentlyReading(BaseModel):
    book_id: str
    book_club_book_id:str
    title: str
    small_img_url: str
    author_names: list
    chapters: int | None = None

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

class CreateUpdatePost(BaseModel):
    user: dict
    chapter: int
    response: Optional[str] = Field(None, max_length = settings.LARGE_TEXT_LENGTH) 
    headline: Optional[str] = Field(None, max_length = settings.SMALL_TEXT_LENGTH) 
    quote: Optional[str] = Field(None, max_length = settings.SMALL_TEXT_LENGTH) 
    id: str
    
class UpdatePost(Post):
    chapter: int
    response: str
    headline: str = ""
    type: str = "club_update"
    quote: str = None
    awards: dict | None = None

class CreateReviewPost(BaseModel):
    user: dict
    headline: str = Field("", max_length = settings.SMALL_TEXT_LENGTH) 
    questions: list[str] = []
    question_ids: list[int] = []
    responses: list[str] = []
    rating: int
    id: str
    book_club_book_id: str

    @validator('questions', each_item=True)
    def check_length_questions(cls, v):
        if len(v) > settings.MEDIUM_TEXT_LENGTH:
            raise ValueError(f"Each string in questions must be at most {settings.MEDIUM_TEXT_LENGTH} characters long")
        return v

    @validator('responses', each_item=True)
    def check_length_responses(cls, v):
        if len(v) > settings.LARGE_TEXT_LENGTH:
            raise ValueError(f"Each string in responses must be at most {settings.LARGE_TEXT_LENGTH} characters long")
        return v
    
    @validator('rating')
    def check_rating(cls, v):
        if v not in [0, 1, 2]:
            raise ValueError("Value must be 0, 1, or 2")
        
        return v
    
class CreateReviewPostNoText(BaseModel):
    rating: Optional[int]
    book_club_book_id: str
    
    @validator('rating')
    def check_rating(cls, v):
        if v not in [0, 1, 2, None]:
            raise ValueError("Value must be 0, 1, or 2, None")
        
        return v
    
class UpdatePostNoText(Post):
    type: str = "club_update_no_text"
    awards: dict | None = None
    
class ReviewPost(Post):
    headline: str 
    questions: list[str] = []
    question_ids: list[int] = []
    responses: list[str] = []
    rating: int
    type: str = "club_review" 
    awards: dict | None = None
    
class ReviewPostNoText(Post):
    type: str = "club_review_no_text"
    awards: dict | None = None
    rating: int | None

class BaseAward(BaseModel):
    id: str
    name: str
    type: str
    description: str
    allowed_uses: int

class Award(BaseAward):
    current_uses: int | None = None

class AwardWithGrants(BaseAward):
    current_uses: int | None = None
    grants: List
    cls: str | None = None

class CreateAward(BaseModel):
    post_id: str
    award_id: str
    user_id: str
    book_club_id: str

class DeleteAward(CreateAward):
    pass

# Notifications!
# Use these to bug the shit out of your friends (with consent)!
class ClubNotificationCreate(BaseModel):
    member_id: str
    # notification_type is a string, can only be "peer-pressure"
    notification_type: Literal['peer-pressure', 'finished-reading']
    sent_by_user_id: str
    book_club_id: str

class ClubNotification(BaseModel):
    id: str
    notification_type: Literal['peer-pressure', 'finished-reading']
    created_date: datetime
    member_id: str
    sent_by_user_username: str
    sent_by_user_id: str
    book_club_id: str
    dismissed: bool = False

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v