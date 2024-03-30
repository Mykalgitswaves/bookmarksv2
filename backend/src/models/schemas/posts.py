from pydantic import BaseModel, validator
import datetime
from neo4j.time import DateTime as Neo4jDateTime
from src.models.schemas.books import BookPreview

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

class ReviewCreate(PostCreate):
    headline: str = ""
    questions: list[str] = []
    question_ids: list[int] = []
    responses: list[str] = []
    spoilers: list[bool] = []
    

class ReviewPost(Post):
    questions: list
    question_ids: list
    responses: list
    spoilers: list
    headline: str = ""
    type: str = "review"
    
class UpdateCreate(PostCreate):
    page: int
    response: str
    spoiler: bool
    headline: str = ""
    quote: str = ""


class UpdatePost(Post):
    page: int
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
