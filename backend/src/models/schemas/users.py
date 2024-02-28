import datetime

from pydantic import BaseModel, EmailStr, validator, Extra
from neo4j.time import DateTime as Neo4jDateTime

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class UserToken(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    username: str
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

class UserUsername(BaseModel):
    username: str

class UserBio(BaseModel):
    bio: str

class UserEmail(BaseModel):
    email: EmailStr

class UserProfileImg(BaseModel):
    profile_img_url: str

class UserPassword(BaseModel):
    password: str
