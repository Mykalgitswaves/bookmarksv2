from pydantic import BaseModel, validator, Field
import datetime
from neo4j.time import DateTime as Neo4jDateTime

from src.config.config import settings

class CommentCreate(BaseModel):
    post_id: str
    username: str
    text: str = Field(..., max_length=settings.LARGE_TEXT_LENGTH)
    user_id: str = ""
    replied_to:str | None = None

class LikedComment(BaseModel):
    username: str
    comment_id: str

class PinnedComment(LikedComment):
    post_id: str

class Comment(CommentCreate):
    id: str
    created_date: datetime.datetime
    liked_by_current_user: bool = False
    posted_by_current_user: bool = False
    deleted: bool = False
    pinned: bool = False
    likes: int = 0
    num_replies: int = 0

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v