from typing import ClassVar, Optional, List

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel, ClassList

"""
ModelsModelsModelsModels for Neo4j
"""


"""
ModelsModelsModelsModels for Request Bodies of Neo4J models (we might not need this)
"""

class UserRequest(BaseModel):
    def __init__(self, **kargs):
        self.fullname = fullname
        self.name = name
        self.genre = ClassList[str]
    
    



"""
Connect to database
"""

app = FastAPI()

@app.get("/")
async def get_data():
    data = {"cashmoney": "cashmoeny"}
    return data

@app.post("/users/{user}")
async def create_user(user: UserRequest, params):
    user = params
    user = UserRequest(fullname=str(request.body.fullname), name=str(request.body.name))
    return user

# user1 = User(fullname="Cash", name="cash")

# user1.merge()