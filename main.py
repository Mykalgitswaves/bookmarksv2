import json
from database.db_helpers import (
    User,
    Review,
    Book,
    Author,
    Genre,
    Tag,
    Neo4jDriver
)
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Dict, List, Annotated
from pydantic import BaseModel
from datetime import datetime, timedelta
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
with open("config.json","r") as f:
    CONFIG = json.load(f)

ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=CONFIG['schemes'], deprecated="auto")

origins = [
    "http://localhost:5174",
    "http://localhost:5173",
    "http://localhost:5173/",
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

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

def get_user(username: str):
    driver = Neo4jDriver()
    user = driver.pull_user_by_username(username=username)
    return(user)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, CONFIG['SECRET_KEY'], algorithm=CONFIG['ALGORITHM'])
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, CONFIG['SECRET_KEY'], algorithms=[CONFIG['ALGORITHM']])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    driver = Neo4jDriver()
    current_user = driver.pull_user_node(current_user.user_id)
    return current_user

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
            
@app.post("/create-login", response_model=Token)
async def post_create_login_user(request: Request = Annotated[OAuth2PasswordRequestForm, Depends()]):
        """
        create user and then login as user with authenticated session
        """
        form_data = await request.json()

        full_name = form_data.get("full_name")
        username = form_data.get("username")
        password = get_password_hash(form_data.get("password"))
        
        driver = Neo4jDriver()
        user = driver.create_user(username=username, password=password)

        authenticate_user(username, password)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}, RedirectResponse(url="/setup-reader/me", status_code=301)

@app.get("/setup-reader/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Redirected endpoint for decorate reader views, provides with correct context/maybe we want to store uuid in the params of url instead
    might be less secure.
    """
    driver = Neo4jDriver()
    current_user = driver.pull_user_node(current_user.user_id)
    return current_user