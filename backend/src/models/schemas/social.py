from pydantic import BaseModel, validator
import datetime
from neo4j.time import DateTime as Neo4jDateTime

class FriendRequestCreate(BaseModel):
    from_user_id: str
    to_user_id: str


class FriendUser(BaseModel):
    id: str
    username: str
    disabled: bool
    created_date: datetime.datetime
    profile_img_url: str | None = None
    relationship_to_current_user: str 

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v
    
class BlockedUser(BaseModel):
    id: str
    username: str
    disabled: bool
    created_date: datetime.datetime
    profile_img_url: str | None = None
    relationship_to_current_user: str 

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v

class FriendRequest(BaseModel):
    from_user: FriendUser
    created_date: datetime.datetime

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v
    
class FollowUserCreate(BaseModel):
    from_user_id: str
    to_user_id: str

class BlockUserCreate(BaseModel):
    from_user_id: str
    to_user_id: str

class FriendDelete(BaseModel):
    from_user_id: str
    to_user_id: str

class BaseActivity(BaseModel):
    acting_user_id: str 
    acting_user_username: str
    acting_user_profile_img_url: str | None = None
    created_date: datetime.datetime

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v
    
class FriendActivity(BaseActivity):
    activity_type: str = "friendship"

class LikedPostActivity(BaseActivity):
    post_id: str
    activity_type: str = "liked_post"
    book_small_img_urls: list[str] | str | None = None

class LikedCommentActivity(BaseActivity):
    comment_id: str
    post_id: str
    comment_text: str
    activity_type: str = "liked_comment"
    book_small_img_urls: list[str] | str | None = None
    
class CommentedOnPostActivity(BaseActivity):
    post_id: str
    comment_id: str
    comment_text: str
    activity_type: str = "commented_on_post"
    book_small_img_urls: list[str] | str | None = None

class RepliedToCommentActivity(BaseActivity):
    post_id: str
    comment_id: str
    reply_id: str
    reply_text: str
    activity_type: str = "replied_to_comment"
    book_small_img_urls: list[str] | str | None = None

class PinnedCommentActivity(BaseActivity):
    post_id: str
    comment_id: str
    comment_text: str
    activity_type: str = "pinned_comment"
    book_small_img_urls: list[str] | str | None = None

class SuggestedFriend(BaseModel):
    user_id: str
    user_username: str
    user_profile_img_url: str
    n_mutual_friends: int