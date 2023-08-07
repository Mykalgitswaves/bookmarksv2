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
from database.auth import verify_access_token

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.encoders import jsonable_encoder
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Dict, List, Annotated
from pydantic import BaseModel
from datetime import datetime, timedelta

"""

Connect to database

Steps for starting uvicorn server: 

    0) SSH Into Kyles server with secret saucy pw

    1) Activate venv with command from base dir(Bookmarks3/) of project:
        '$ conda activate bookmarks'
    
        #NOTE: if you ever need to deactivate just type deactivate 
        
    2) Once, inside your venv run this command inside the same shell: 
        '$ uvicorn main:app --reload'

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
security = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
with open("config.json","r") as f:
    CONFIG = json.load(f)

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # expire in one day

pwd_context = CryptContext(schemes=CONFIG['schemes'], deprecated="auto")

origins = [
    "http://localhost:5174",
    "http://localhost:5173",
    "http://localhost:5173/",
    "http://localhost:5173/*",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["PUT", "GET", "POST", "DELETE"],
)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

def get_user(username: str):
    driver = Neo4jDriver()
    user = driver.pull_user_by_username(username=username)
    driver.close()
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
    driver.close()
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    driver = Neo4jDriver()
    current_user = driver.pull_user_node(current_user.user_id)
    driver.close()
    return current_user

@app.get("/books")
async def get_books(skip: int = 0, limit: int = 3):
    """
    Used for initial fetch 
    """
    driver = Neo4jDriver()
    result = driver.pull_n_books(skip, limit)
    driver.close()
    return result

@app.get("/books/{text}")
async def get_books_by_title(text: str, skip: int=0, limit: int=3):
    """
    Search a damn book
    """
    driver = Neo4jDriver()
    result = driver.pull_search2_books(text=text, skip=skip, limit=limit)
    driver.close()
    return result

@app.get("/genres/{text}")
async def get_genres_by_title(text: str, skip: int=0, limit: int=3):
    """
    Search for a genre by text
    """
    driver = Neo4jDriver()
    result = driver.pull_search2_genre(text=text, skip=skip, limit=limit)
    driver.close()
    return result

@app.get("/authors/{text}")
async def get_authors_by_title(text: str, skip: int=0, limit: int=3):
    """
    Search for an author by text
    """
    driver = Neo4jDriver()
    result = driver.pull_search2_author(text=text, skip=skip, limit=limit)
    driver.close()
    return result
            
@app.post("/create-login", response_model=Token)
async def post_create_login_user(form_data:Annotated[OAuth2PasswordRequestForm, Depends()]):
        """
        create user and then login as user with authenticated session
        """
        print(form_data)
        password = get_password_hash(form_data.password)
        username = form_data.username
        print(username, password, form_data)

        if username and password:
            driver = Neo4jDriver()
            user = driver.create_user(username=username, password=password)

            authenticate_user(form_data.username, password)
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.user_id}, expires_delta=access_token_expires
            )
            driver.close()
            return {"access_token": access_token, "token_type": "bearer"} #, RedirectResponse(url="/setup-reader/me", status_code=301)

@app.get("/setup-reader/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Redirected endpoint for decorate reader views, provides with correct context/maybe we want to store uuid in the params of url instead
    might be less secure.
    """
    driver = Neo4jDriver()
    current_user = driver.pull_user_node(current_user.user_id)
    driver.close()
    return current_user


def verify_access_token_2(access_token: str):
        decoded_token = jwt.decode(access_token, CONFIG['SECRET_KEY'], algorithms=[CONFIG['ALGORITHM']], options={"verify_sub": False})
        return decoded_token
 


@app.put("/setup-reader/books")
async def put_users_me_books(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    access_token = credentials.credentials

    if not access_token:
        raise HTTPException(status_code=401, detail="Missing session cookie")

    # Verify the access token
    if access_token.startswith('session_token='):
        access_token = access_token[len('session_token='):]
    decoded_token = verify_access_token_2(access_token)

    user_id = decoded_token['sub']
    
    book_array = await request.json()

    driver = Neo4jDriver()
    user =  driver.pull_user_node(user_id=user_id)
    for book in book_array:
        user.add_reviewed_setup(book_id=int(book['id']), rating=int(book['review']))
    driver.close()
    return {"user": user}

@app.put("/setup-reader/genres")
async def put_users_me_genres(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    access_token = credentials.credentials

    if not access_token:
        raise HTTPException(status_code=401, detail="Missing session cookie")

    # Verify the access token
    if access_token.startswith('session_token='):
        access_token = access_token[len('session_token='):]
    decoded_token = verify_access_token_2(access_token)

    user_id = decoded_token['sub']
    
    genres = await request.json()

    driver = Neo4jDriver()
    user =  driver.pull_user_node(user_id=user_id)
    for genre in genres:
        user.add_favorite_genre(genre_id=int(genre['id']))
    driver.close()
    return {"user": user}

@app.put("/setup-reader/authors")
async def put_users_me_authors(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    access_token = credentials.credentials

    if not access_token:
        raise HTTPException(status_code=401, detail="Missing session cookie")

    # Verify the access token
    if access_token.startswith('session_token='):
        access_token = access_token[len('session_token='):]
    decoded_token = verify_access_token_2(access_token)

    user_id = decoded_token['sub']
    
    authors = await request.json()

    driver = Neo4jDriver()
    user =  driver.pull_user_node(user_id=user_id)
    for author in authors:
        user.add_favorite_author(author_id=int(author['id']))
    driver.close()
    
    return JSONResponse(content={"user_id": jsonable_encoder(user.user_id)})

@app.get("/feed/{user_id}")
async def get_user_home_feed(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    After a user submits to put_decorate_reader_create endpoint they are redirected to their home feed which is a profile page containing information gathered from the set up of their profile. It should return information about the User. Also, they need to have a cookie to access this endpoint so even if someone guesses the correct uuid unless they have a cookie they wont be able to access any sensitive information. In the case they dont have cookie we redirect to sign in / sign up page.
    """

@app.get("/api/search/{param}")
async def search_for_param(param: str, skip: int=0, limit: int=10):
    """
    Endpoint used for searching for users, todo add in credentials for searching
    """
    print(param)
    driver = Neo4jDriver()
    search_result = driver.search_for_param(param=param, skip=skip, limit=10)
    driver.close()
    
    print(search_result)

    return JSONResponse(content={"data": jsonable_encoder(search_result)})
