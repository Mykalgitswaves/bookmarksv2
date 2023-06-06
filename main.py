from database.db_helpers import (
    User,
    Review,
    Book,
    Author,
    Genre,
    Tag,
    Neo4jDriver
)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from typing import Dict, List
"""

Connect to database

Steps for starting uvicorn server: 
    1) Activate venv with command from base dir(Bookmarks3/) of project:
        'conda activate bookmarks '
    
        #NOTE: if you ever need to deactivate just type deactivate 
        
    2) Once, inside your venv run this command inside the same shell: 
        'uvicorn main:app --reload'

    This command ^ will automatically reload after any changes made to main.py, which for our purposes has the endpoints to our app for now. 
    
    We might want to at somepoint, move the business logic outside of the main.py file like you we have in /database directory.
    
    3) Once running to see the actual endpoints go into the server that is printed in your terminal and enter this param into the url:
        'http://127.0.0.1:8000/docs#/'

    The /docs#/ page/feature of fastapi lets you test your endpoints locally, really great for seeing where things are fucked up and why. 

    4) Click on the endpoint you have created, in the browser and select try it out, as we start building up endpoints we can start to get into the jazz of FastApi library, there is a lot of cool shit in here.

    5) The only other thing i can think of rn is that we will need to set up our backend cors policies to allow for our spa frontend to request to api. We can work on that together.

    6) Install dependencies with pip inside conda. For more cash money chix.

"""

app = FastAPI()

origins = [
    "http://localhost:5174",
    "http://localhost:5173",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/user-test")
async def get_test_user_data():
    driver = Neo4jDriver()
    result = driver.pull_user_node(user_id=1)
    return result

@app.get("/books")
async def get_books(skip: int = 0, limit: int = 3):
    """
    Used for initial fetch 
    """
    driver = Neo4jDriver()
    result = driver.pull_n_books(skip, limit)
    return result

@app.get("/books/{text}")
async def get_books_by_title(text: str, skip: int=0, limit: int=3):
    """
    Search a damn book
    """
    driver = Neo4jDriver()
    result = driver.pull_search2_books(text=text, skip=skip, limit=limit)
    return result

@app.get("/genres/{text}")
async def get_genres_by_title(text: str, skip: int=0, limit: int=3):
    """
    Search for a genre by text
    """
    driver = Neo4jDriver()
    result = driver.pull_search2_genre(text=text, skip=skip, limit=limit)
    return result

@app.get("/authors/{text}")
async def get_authors_by_title(text: str, skip: int=0, limit: int=3):
    """
    Search for an author by text
    """
    driver = Neo4jDriver()
    result = driver.pull_search2_author(text=text, skip=skip, limit=limit)
    return result

@app.post("/post-create-reader/")
async def post_create_user(user_data: Dict):
    print(user_data.items())
    
            # Perform any necessary operations with each user data
            
