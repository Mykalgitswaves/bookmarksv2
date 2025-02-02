from pydantic import BaseModel, validator, Field
import datetime
from neo4j.time import DateTime as Neo4jDateTime
from typing import Optional, List

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
    replies: Optional[List['Comment']] = []

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v
    

def process_replies(reply_data, post_id: str):
    """Recursively process replies and their nested replies"""
    if not reply_data or not isinstance(reply_data, dict):
        return []
    
    # Get replied_to with a default empty list
    replied_to = reply_data.get('replied_to', []) or []
    
    replies = []
    for reply in replied_to:
        # Skip invalid replies
        if not reply:
            continue

        try:
            reply_obj = Comment(
                id=reply['id'],
                post_id=post_id,
                text=reply['text'],
                created_date=reply['created_date'],
                username=reply.get('commenter', ''),
                user_id=reply.get('commenter_id', ''),
                likes=reply.get('likes', 0),
                is_reply=reply.get('is_reply', True),
                pinned=reply.get('pinned', False),
                deleted=reply.get('deleted', False),
                liked_by_current_user=reply.get('liked_by_current_user', False),
                posted_by_current_user=reply.get('posted_by_current_user', False),
                num_replies=len(reply.get('replied_to', [])),
                replies=process_replies(reply_data=reply, post_id=post_id)
            )
            replies.append(reply_obj)
        except Exception as e:
            print(f"Error processing reply: {e}")
            print(f"Reply data: {reply}")
            continue
    
    return replies

def build_comment_thread(record, post_id: str):
    """Build the complete comment thread structure"""
    thread = record['comment_thread']
    
    # Check if we have a valid comment
    if not thread or 'comment' not in thread:
        return None
        
    comment = thread['comment']
    
    # Handle both Node objects and dictionary properties
    comment_props = comment.get('properties', comment) if isinstance(comment, dict) else comment
    
    # Safely get the number of replies
    replies_obj = thread.get('replies') or {}
    num_replies = len(replies_obj.get('replied_to', [])) if isinstance(replies_obj, dict) else 0
    
    try:
        # Build the top-level comment structure
        comment_tree = Comment(
            id=comment_props['id'],
            text=comment_props['text'],
            created_date=thread['created_date'],
            username=thread['commenter'],
            user_id=thread['commenter_id'],
            liked_by_current_user=thread['liked'],
            posted_by_current_user=thread.get('posted_by_current_user', False),
            likes=comment_props.get('likes', 0),
            is_reply=comment_props.get('is_reply', False),
            pinned=comment_props.get('pinned', False),
            deleted=comment_props.get('deleted', False),
            num_replies=num_replies,
            post_id=post_id,
            replies=[]
        )
        
        # Process replies if they exist and are valid
        if thread.get('replies') and isinstance(thread['replies'], dict):
            comment_tree.replies = process_replies(reply_data=thread['replies'], post_id=post_id)
        
        return comment_tree
    except Exception as e:
        print(f"Error building comment thread: {e}")
        print(f"Thread data: {thread}")
        return None