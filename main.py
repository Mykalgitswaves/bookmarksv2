from typing import ClassVar, Optional, List

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel

"""
ModelsModelsModelsModels for Neo4j
"""


"""
ModelsModelsModelsModels for Request Bodies of Neo4J models (we might not need this)
"""

class UserRequest(BaseModel):
    def __init__(self, fullname:str, name:str):
        self.fullname = fullname
        self.name = name
    
    



"""
Connect to database
"""

app = FastAPI()

@app.get("/")
async def get_data():
    data = {"cashmoney": "cashmoeny"}
    return data

@app.post("/users/")
async def create_user(user: UserRequest, request):
    user = UserRequest(fullname=str(request.body.fullname), name=str(request.body.name))
    return user

# user1 = User(fullname="Cash", name="cash")

# user1.merge()