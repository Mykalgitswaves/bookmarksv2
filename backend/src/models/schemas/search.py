from pydantic import BaseModel
from src.models.schemas.social import FriendUser

class SearchSchema(BaseModel):
    param: str

class SearchResultUser(FriendUser):
    pass