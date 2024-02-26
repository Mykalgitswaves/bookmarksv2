from pydantic import BaseModel, validator
import datetime
from neo4j.time import DateTime as Neo4jDateTime

class CommentCreate(BaseModel):
    post_id: str
    username: str
    text: str
    user_id: str = ""
    replied_to:str | None = None

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