from pydantic import BaseModel, validator, Field
from typing_extensions import Annotated
import datetime
from neo4j.time import DateTime as Neo4jDateTime
from src.models.schemas.books import BookPreview
from src.config.config import settings

class PostCreate(BaseModel):
    book: BookPreview
    user_username: str

class LikedPost(BaseModel):
    username: str
    post_id: str

class Post(BaseModel):
    id: str
    book: BookPreview
    created_date: datetime.datetime
    user_username: str = ""
    user_id: str = ""
    comments: list = []
    likes: int = 0
    liked_by_current_user: bool = False
    posted_by_current_user: bool = False
    num_comments: int = 0
    deleted: bool = False

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v
    
class WantToReadCreate(BaseModel):
    user_id: str
    book_id: str
    headline: str | None = None

class CurrentlyReadingCreate(BaseModel):
    user_id: str
    book_id: str
    headline: str | None = None

class ReviewCreate(PostCreate):
    headline: str = Field("", max_length = settings.SMALL_TEXT_LENGTH) 
    questions: list[str] = []
    question_ids: list[int] = []
    responses: list[str] = [] 
    spoilers: list[bool] = []
    rating: int | None = None

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

class WantToReadPost(Post):
    headline: str = ""
    type: str = "want_to_read_post"

class CurrentlyReadingPost(Post):
    headline: str = ""
    type: str = "currently_reading_post"

class ReviewPost(Post):
    questions: list
    question_ids: list
    responses: list
    spoilers: list
    headline: str = ""
    type: str = "review"
    rating: int | None = None
    
class UpdateCreate(PostCreate):
    page: int = Field(..., ge = 0, le=10000)
    chapter: int = Field(..., ge = 0, le=10000)
    response: str = Field("", max_length = settings.LARGE_TEXT_LENGTH) 
    spoiler: bool
    headline: str = Field("", max_length = settings.SMALL_TEXT_LENGTH) 
    quote: str = Field("", max_length = settings.MEDIUM_TEXT_LENGTH) 


class UpdatePost(Post):
    page: int
    chapter: int | None = None
    response: str
    spoiler: bool
    headline: str = ""
    type: str = "update"
    quote: str = None

class ComparisonCreate(BaseModel):
    user_username: str
    compared_books: list[BookPreview]
    comparators: list[str]
    comparator_ids: list[str]
    responses: list[str]
    book_specific_headlines: list[str]

    @validator('comparators', each_item=True)
    def check_length_comparators(cls, v):
        if len(v) > settings.SMALL_TEXT_LENGTH:
            raise ValueError(f"Each string in comparators must be at most {settings.SMALL_TEXT_LENGTH} characters long")
        return v

    @validator('responses', each_item=True)
    def check_length_responses(cls, v):
        if len(v) > settings.LARGE_TEXT_LENGTH:
            raise ValueError(f"Each string in responses must be at most {settings.LARGE_TEXT_LENGTH} characters long")
        return v
    
    @validator('book_specific_headlines', each_item=True)
    def check_length_book_specific_headlines(cls, v):
        if len(v) > settings.SMALL_TEXT_LENGTH:
            raise ValueError(f"Each string in book_specific_headlines must be at most {settings.SMALL_TEXT_LENGTH} characters long")
        return v

class ComparisonPost(BaseModel):
    id: str
    created_date: datetime.datetime
    user_username: str = ""
    user_id: str = ""
    compared_books: list[BookPreview]
    comparators: list[str]
    comparator_ids: list[int]
    responses: list[str]
    book_specific_headlines: list[str]
    comments: list = []
    likes: int = 0
    liked_by_current_user: bool = False
    posted_by_current_user: bool = False
    num_comments: int = 0
    deleted: bool = False
    type: str = "comparison"

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v
    
class RecommendationFriendCreate(PostCreate):
    to_user_username: str
    from_user_text: str
    to_user_text: str


class RecommendationFriend(Post):
    to_user_username: str
    from_user_text: str
    to_user_text: str
    type: str = "friend_recommendation"

class MilestoneCreate(BaseModel):
    user_username: str
    num_books: int

class MilestonePost(BaseModel):
    id: str
    created_date: datetime.datetime
    user_username: str
    num_books: int
    user_id: str = ""
    comments: list = []
    likes: int = 0
    liked_by_current_user: bool = False
    posted_by_current_user: bool = False
    num_comments: int = 0
    deleted: bool = False
    type: str = "milestone"

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v
