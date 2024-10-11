import datetime

from pydantic import BaseModel, EmailStr, validator, Extra, Field
from neo4j.time import DateTime as Neo4jDateTime
from src.config.config import settings

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=settings.XSMALL_TEXT_LENGTH)
    password: str = Field(..., min_length=8, max_length=settings.XSMALL_TEXT_LENGTH)
    email: EmailStr

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class UserToken(BaseModel):
    username: str
    password: str

class BaseUser(BaseModel):
    id: str
    username: str
    email: EmailStr
    disabled: bool = False

class User(BaseUser):
    profile_img_url: str = None
    created_date: datetime.datetime

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v
    
    class Config:
        extra=Extra.allow
    
class UserWithPassword(BaseModel):
    id: str
    username: str
    password: str
    email: EmailStr
    disabled: bool
    created_date: datetime.datetime
    profile_img_url: str = None

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v

class UserInResponse(User):
    token: str
    token_type: str = 'bearer'

class UserSettings(User):
    full_name : str | None
    bio : str | None
    relationship_to_current_user : str | None

class UserAboutMe(BaseModel):
    genres: set[tuple[str, str]] = set()
    authors: set[tuple[str, str]] = set()

class UserId(BaseModel):
    id: str

class UserUsername(BaseModel):
    username: str = Field(..., min_length=3, max_length=settings.XSMALL_TEXT_LENGTH)

class UserBio(BaseModel):
    bio: str = Field(..., max_length=settings.MEDIUM_TEXT_LENGTH)

class UserEmail(BaseModel):
    email: EmailStr

class UserProfileImg(BaseModel):
    profile_img_url: str

class UserPassword(BaseModel):
    password: str

class Member(BaseUser):
    role: str
