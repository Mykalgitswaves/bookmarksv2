from pydantic import BaseModel

class SearchSchema(BaseModel):
    param: str