import json
from database.db_helpers import (
    User,
    ReviewPost,
    UpdatePost,
    ComparisonPost,
    MilestonePost,
    RecommendationFriend,
    Book,
    Author,
    Genre,
    Tag,
    Comment,
    Neo4jDriver
)
from database.api.books_api.search import BookSearch
from database.api.books_api.add_book import pull_google_book
from database.api.books_api.book_versions import search_versions_by_metadata
from database.auth import verify_access_token

from db_tasks import update_book_google_id, pull_book_and_versions

from fastapi import FastAPI, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi import Query
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

    
Retrieving user data from access token

The get_current_user function is responsible for validating a user given the access token. It works in conjunction with get_current_active_user
to validate that the user is not disable (not like ADA or anything). 

To retrieve this in an endpoint, pass current_user: Annotated[User, Depends(get_current_active_user)] as an argument
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

# Single driver that we start
driver = Neo4jDriver()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

def get_user(username: str):
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

@app.post("/api/token")
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
    
    return {"token":{"access_token": access_token, "token_type": "bearer"}, "user":{"uuid":user.user_id}}

@app.post("/token")
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
    # NEed to retunr user.user_id for routing here @Kyle.
    return {"token":{"access_token": access_token, "token_type": "bearer"}, "user":{"uuid":user.user_id}}

@app.post("/api/create-login", response_model=Token)
async def post_create_login_user(form_data:Annotated[OAuth2PasswordRequestForm, Depends()]):
        """
        create user and then login as user with authenticated session
        """
        # print(form_data)
        password = get_password_hash(form_data.password)
        username = form_data.username
        # print(username, password, form_data)

        if username and password:
            try:
                user = driver.create_user(username=username, password=password)

                authenticate_user(form_data.username, password)
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    data={"sub": user.username}, expires_delta=access_token_expires
                )
                return {"access_token": access_token, "token_type": "bearer"}
            except:
                network_error = HTTPException(
                status_code=404,
                detail="Network error occurred during login, please try again later",
                headers={"WWW-Authenticate": "Bearer"},
                )
                return network_error
        else:
            password_error = HTTPException(
                status_code=401,
                detail="Please enter a valid username and password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            return password_error

@app.put("/setup-reader/name")
async def setup_user_name(request: Request, current_user: Annotated[User, Depends(get_current_active_user)]):
    name = await request.json()
    if current_user:
        try:
            user = driver.put_name_on_user(username=current_user.username, full_name=name)
            
            if user is not None:
                return HTTPException(
                    status_code=200,
                    detail="SUCCESS DUDE"
                )

        except:
            return HTTPException(
                status_code=500,
                detail="Internal error, try again later"
            )

def verify_access_token_2(access_token: str):
        decoded_token = jwt.decode(access_token, CONFIG['SECRET_KEY'], algorithms=[CONFIG['ALGORITHM']], options={"verify_sub": False})
        return decoded_token

@app.get("/api/auth_user")
async def verify_user(request: Request, current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Verifies if the user has a current access token and if the access token is equivalent to the uuid
    """
    uuid = request.query_params['uuid']
    if uuid and current_user:
        if uuid == current_user.user_id:
            return HTTPException(status_code=200, detail="User is validated") # User is validated
        else:
            validation_error = HTTPException(
                status_code=401,
                detail="uuid and access token dont match",
                headers={"WWW-Authenticate": "Bearer"},
            )
            return validation_error
    else:
        validation_error = HTTPException(
                status_code=401,
                detail="Missing uuid or access token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return validation_error

@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Returns the current user data, requires the get_current_active_user to validate the user from a token 
    """
    return current_user

@app.put("/setup-reader/books")
async def put_users_me_books(request: Request, current_user: Annotated[User, Depends(get_current_active_user)]):
    book_array = await request.json()
    try:
        for book in book_array:
            current_user.add_reviewed_setup(book_id=int(book['id']), rating=int(book['review']))

    except:
        network_error = HTTPException(
                status_code=404,
                detail="Network error occurred during setup, please try again later",
                headers={"WWW-Authenticate": "Bearer"},
                )
        return network_error

@app.put("/setup-reader/genres")
async def put_users_me_genres(request: Request, current_user: Annotated[User, Depends(get_current_active_user)]):
    genres = await request.json()

    try:
        for genre in genres:
            current_user.add_favorite_genre(genre_id=int(genre['id']),driver=driver)

    except:
        network_error = HTTPException(
                status_code=404,
                detail="Network error occurred during setup, please try again later",
                headers={"WWW-Authenticate": "Bearer"},
                )
        return network_error

@app.put("/setup-reader/authors")
async def put_users_me_authors(request: Request, current_user: Annotated[User, Depends(get_current_active_user)]):
    authors = await request.json()
    try:
        for author in list(authors):
            current_user.add_favorite_author(author_id=int(author),driver=driver)
    except:
        network_error = HTTPException(
                status_code=404,
                detail="Network error occurred during setup, please try again later",
                headers={"WWW-Authenticate": "Bearer"},
                )
        return network_error
    return JSONResponse(content={"uuid": jsonable_encoder(current_user.user_id)})


@app.get("/books")
async def get_books(skip: int = 0, limit: int = 3):
    """
    Used for initial fetch 
    """
    result = driver.pull_n_books(skip, limit)
    return result

@app.get("/books/n")
async def get_books_by_n(request: Request, skip: int=0, limit:int=5, by_n=True):
    """
    Used to grab a certain amount of books
    """
    request_limit = int(request.query_params['limit'])
    result = driver.pull_n_books(skip, limit=request_limit, by_n=by_n)
    return JSONResponse(content={"data": jsonable_encoder(result)}) 

@app.get("/books/{text}")
async def get_books_by_title(text: str, skip: int=0, limit: int=3):
    """
    Search a damn book
    """
    result = driver.pull_search2_books(text=text, skip=skip, limit=limit)
    return JSONResponse(content={"data": jsonable_encoder(result)}) 

@app.get("/api/books/{book_id}")
async def get_book_page(book_id: str, background_tasks:BackgroundTasks):
    """
    Endpoint for book page. If a google id is used, the canonical version of the book is returned
    """
    if book_id[0] == 'g':
        # Checks if the book is already in our database
        book = driver.get_book_by_google_id_flexible(book_id)
        if not book:
            # Pulls the book down otherwise
            book = pull_google_book(book_id, driver)
            background_tasks.add_task(pull_book_and_versions,book,driver)
    else:
        book = driver.pull_book_node(book_id=book_id)
        
    return JSONResponse(content={"data": jsonable_encoder(book)})

@app.get("/api/books/{book_id}/similar")
async def get_book_page(book_id: int):
    """
    Endpoint for similar book=
    """
    books = driver.pull_similar_books(book_id=book_id)
    return JSONResponse(content={"data": jsonable_encoder(books)})

@app.get("/genres/{text}")
async def get_genres_by_title(text: str, skip: int=0, limit: int=3):
    """
    Search for a genre by text
    """
    result = driver.pull_search2_genre(text=text, skip=skip, limit=limit)
    return result


@app.get("/authors/{text}")
async def get_authors_by_title(text: str, skip: int=0, limit: int=3):
    """
    Search for an author by text
    """
    result = driver.pull_search2_author(text=text, skip=skip, limit=limit)
    return result
            
    
@app.get("/api/author/")
async def get_author_page(request: Request):
    """
    Get an author from the db for their page. Load related books with this that the author wrote.
    """
    # print(request)
    author_id = int(request.query_params['book'])

    response = driver.pull_author_page_nodes(author_id=author_id)

    return JSONResponse(content={"author": jsonable_encoder(response)})

@app.get("/api/search/{param}")
async def search_for_param(param: str, skip: int=0, limit: int=5):
    """
    Endpoint used for searching for users, todo add in credentials for searching
    """
    
    book_search = BookSearch()
    books_result = book_search.search(param, skip, limit)
    search_result = driver.search_for_param(param=param, skip=skip, limit=limit)
    search_result['books'] = books_result
   
    return JSONResponse(content={"data": jsonable_encoder(search_result)})

@app.get("/api/search/book/{param}")
async def search_for_param(param: str, skip: int=0, limit: int=5):
    """
    Endpoint used for searching for users, todo add in credentials for searching
    """
    
    book_search = BookSearch()
    books_result = book_search.search(param, skip, limit)
   
    return JSONResponse(content={"data": jsonable_encoder(books_result)})

@app.post("/api/review/create_review")
async def create_review(request: Request, 
                        current_user: Annotated[User, Depends(get_current_active_user)],
                        background_tasks: BackgroundTasks):
    """
    Creates a post of type Review
    
    {"book_id":,
     "headline":,
     questions:[]
     ids:[]
     responses:[]
     spoilers:[]
     }

    """
    if not current_user:
        raise HTTPException("401","Unauthorized")

    response = await request.json()
    response = response['_value']

    book_id = response['book_id']
    small_img_url = response['small_img_url']
    title = response['title']
    
    if book_id[0] == "g":
        db_book = driver.get_id_by_google_id(book_id) 
        if db_book:
            book_id = db_book['id']
            small_img_url = db_book['small_img_url']
            title = db_book['title']

    review = ReviewPost(
                    post_id='', 
                    book=book_id,
                    user_username=current_user.username,
                    book_title=title,
                    book_small_img=small_img_url,
                    headline=response['headline'],
                    questions=response['questions'],
                    question_ids=response['ids'],
                    responses=response['responses'],
                    spoilers=response['spoilers']
            )
    review.create_post(driver)

    if book_id[0] == "g":
        background_tasks.add_task(update_book_google_id,book_id,driver)

    return JSONResponse(content={"data": jsonable_encoder(review)})

@app.post("/api/review/create_update")
async def create_update(request: Request, 
                        current_user: Annotated[User, Depends(get_current_active_user)],
                        background_tasks: BackgroundTasks):
    """
    Creates a post of type Update
    
    {"book_id":,
     "headline":,
     "page",
     questions:[]
     ids:[]
     responses:[]
     spoilers:[]
     }

    """
    if not current_user:
        raise HTTPException("401","Unauthorized")

    response = await request.json()
    response = response['_value']

    book_id = response['book_id']
    small_img_url = response['small_img_url']
    title = response['title']

    db_book = driver.get_id_by_google_id(book_id)
    if db_book:
        book_id = db_book['id']
        small_img_url = db_book['small_img_url']
        title = db_book['title']
        
    update = UpdatePost(post_id='',
                        book=book_id,
                        book_title=title,
                        book_small_img=small_img_url,
                        user_username=current_user.username,
                        headline=response['headline'],
                        page=response['page'],
                        response=response['response'],
                        spoiler=response['is_spoiler'])
    
    update.create_post(driver)

    if book_id[0] == "g":
        background_tasks.add_task(update_book_google_id,book_id,driver)


    return JSONResponse(content={"data": jsonable_encoder(update)})

@app.post("/api/review/create_comparison")
async def create_comparison(request: Request, 
                            current_user: Annotated[User, Depends(get_current_active_user)],
                            background_tasks: BackgroundTasks):
    """
    Creates a post of type Comparison
    
    {
     "book_ids":[],
     comparators:[],
     compared_books:[],
     comparator_ids:[],
     responses:[],
     book_specific_headlines:[]
     }
    """
    
    if not current_user:
        raise HTTPException("401","Unauthorized")

    response = await request.json()
    response = response['_value']

    if response["book_ids"][0] == response["book_ids"][1]:
        raise HTTPException("400","Comparisons require two unique books, please select another book for your post.")
    
    book_ids = []
    small_image_urls = []
    titles = []
    
    books_metadata = zip(response['book_ids'],response['book_small_imgs'],response['book_titles'])

    for book_id, small_image_url, title in books_metadata:
        db_book = driver.get_id_by_google_id(book_id)
        if db_book:
            book_ids.append(db_book['id'])
            small_image_urls.append(db_book['small_img_url'])
            titles.append(db_book['titles'])
        else:
            book_ids.append(book_id)
            small_image_urls.append(small_image_url)
            titles.append(title)
            

    comparison = ComparisonPost(post_id='',
                                compared_books=book_ids,
                                user_username=current_user.username,
                                comparators=response['comparator_topics'],
                                comparator_ids=response['comparator_ids'],
                                responses=response['responses'],
                                book_specific_headlines=response['book_specific_headlines'],
                                book_title=titles,
                                book_small_img=small_image_urls)
    
    comparison.create_post(driver)

    for book_id in book_ids:
        if book_id[0] == "g":
            print("Started background task")
            background_tasks.add_task(update_book_google_id,book_id,driver)

    return JSONResponse(content={"data": jsonable_encoder(comparison)})

@app.post("/api/review/create_recommendation_friend")
async def create_recommendation_friend(request: Request, 
                                       current_user: Annotated[User, Depends(get_current_active_user)],
                                       background_tasks: BackgroundTasks):
    """
    Creates a post of type RecommendationFriend
    
    {"book_id":,
     "to_user_username":,
     "from_user_text":,
     "to_user_text":
     }
    """
    if not current_user:
        raise HTTPException("401","Unauthorized")

    response = await request.json()
    response = response['_value']

    book_id = response['book_id']
    small_img_url = response['small_img_url']
    title = response['title']

    db_book = driver.get_id_by_google_id(book_id)
    if db_book:
        book_id = db_book['id']
        small_img_url = db_book['small_img_url']
        title = db_book['title']

    recommendation = RecommendationFriend(post_id='',
                                          book=book_id,
                                          user_username=current_user.username,
                                          to_user_username=response['to_user_username'],
                                          from_user_text=response['from_user_text'],
                                          to_user_text=response['to_user_text'],
                                          book_title=title,
                                          book_small_img=small_img_url)
    
    recommendation.create_post(driver)

    if book_id[0] == "g":
        background_tasks.add_task(update_book_google_id,book_id,driver)

    return JSONResponse(content={"data": jsonable_encoder(recommendation)})

@app.post("/api/review/create_milestone")
async def create_milestone(request: Request, current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Creates a post of type Milestone
    
    {"num_books":
     }
    """
    if not current_user:
        raise HTTPException("401","Unauthorized")

    response = await request.json()
    response = response['_value']
    
    milestone = MilestonePost(post_id='',
                              book="",
                              user_username=current_user.username,
                              num_books=response['num_books'])
    
    milestone.create_post(driver)

    return JSONResponse(content={"data": jsonable_encoder(milestone)})

@app.get("/api/{user_id}/posts")
async def get_user_posts(user_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    if user_id and current_user:
        return(JSONResponse(content={"data": jsonable_encoder(current_user.get_posts(driver))}))

@app.get("/api/{user_id}/posts/{post_id}/post")
async def get_post(post_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    if post_id and current_user:
        data = driver.get_post(post_id=post_id, username=current_user.username)
        post = data["post"]
        user_id = data["user_id"]
        post_type = type(post).__name__
        return (JSONResponse(content={"data": jsonable_encoder({"post": post, "post_type": post_type, "op_user_id": user_id})}))


@app.post("/api/{user_id}/like/comparisons/{comparison_id}")
async def like_comparison_post(user_id: str, comparison_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    if user_id and current_user and comparison_id:
        return (JSONResponse(content={"data": "you liked this shit"}))
    
@app.post("/api/review/create_comment")
async def create_comment(request: Request, current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Endpoint for posting a comment.

    Value 'replied_to' should be None if comment is not a reply to another comment
    """
    if not current_user:
        raise HTTPException("401","Unauthorized")

    response = await request.json()

    comment = Comment(comment_id='',
                        post_id=response['post_id'],
                        username=current_user.username,
                        user_id=current_user.user_id,
                        replied_to=response['replied_to'],
                        text=response['text'])
    
    comment.create_comment(driver)

    comment.posted_by_current_user = True
    
    if not comment.id and not comment.created_date:
        raise HTTPException("410"," Gone - This chapter closes, yet its essence endures beyond the veil")

    return JSONResponse(content={"data": jsonable_encoder(comment)})

@app.put("/api/review/{post_id}/like") # NOT SURE IF THIS MAKES ANY SENSE @MICHAEL
async def like_post(post_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Adds a like to a post. Take the following format.
    """
    
    if not current_user:
        raise HTTPException("401","Unauthorized")

    if post_id:
        driver.add_liked_post(current_user.username, post_id)

@app.put("/api/review/{comment_id}/like") # NOT SURE IF THIS MAKES ANY SENSE @MICHAEL
async def like_comment(comment_id:str, current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Adds a like to a post. Take the following format.
    """

    if not current_user:
        raise HTTPException("401","Unauthorized")
    if comment_id:
        driver.add_liked_comment(current_user.username, comment_id)

@app.get("/api/review/{post_id}/comments")
async def get_comments_for_post(post_id: str, current_user: Annotated[User, Depends(get_current_active_user)], skip: int | None = Query(default=None), limit: int | None = Query(default=None)):
    """
    Gets the comments on a post
    Uses skip and limit for pagination
    """
    if not current_user:
        raise HTTPException("401","Unauthorized")
    if post_id:
        comments = driver.get_all_comments_for_post(post_id=post_id,
                                                    username=current_user.username,
                                                    skip=skip,
                                                    limit=limit)
  
        return JSONResponse(content={"data": jsonable_encoder({"comments": comments['comments'], "pinned_comments": comments['pinned_comments']})})

@app.get("/api/review/comments/{comment_id}/replies")
async def get_all_replies_for_comment(comment_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Returns a list of comments for a specific reply.
    """
    if not current_user:
        raise HTTPException("401", "Unauthorized")
    if comment_id:
        replies = driver.get_all_replies_for_comment(comment_id=comment_id, username=current_user.username)
        return(JSONResponse(content={"data": jsonable_encoder(replies)}))
    
@app.put("/api/review/{comment_id}/pin/{post_id}")
async def pin_comment(comment_id: str, post_id: str, current_user: Annotated[User, Depends(get_current_active_user)]): #@MICHAEL DO WE NEED TO VALIDATE THAT THE CURRENT USER IS THE POST AUTHOR HERE
    """
    Adds a pin to a comment. Take the following format.
    {
    "comment_id":str,
    "post_id":str
    }
    """
    
    if not current_user:
        raise HTTPException("401","Unauthorized")

    driver.add_pinned_comment(comment_id, post_id)

@app.put("/api/review/{comment_id}/remove_like") # NOT SURE IF THIS MAKES ANY SENSE @MICHAEL
async def remove_like_comment(comment_id:str, current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    remove a like to a comment.
    """
    
    if not current_user:
        raise HTTPException("401","Unauthorized")
    
    if comment_id:
        driver.remove_liked_comment(current_user.username, comment_id)

@app.post("/api/review/{post_id}/remove_like") # NOT SURE IF THIS MAKES ANY SENSE @MICHAEL
async def remove_like_post(request: Request, post_id:str, current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    remove a like to a post. 
    """
    
    if not current_user:
        raise HTTPException("401","Unauthorized")
   
    if post_id:
        driver.remove_liked_post(current_user,post_id)

@app.put("/api/review/post/{post_id}/comment/{comment_id}/remove_pin")
async def remove_pin_comment(post_id: str,  comment_id: str, current_user: Annotated[User, Depends(get_current_active_user)]): #@MICHAEL DO WE NEED TO VALIDATE THAT THE CURRENT USER IS THE POST AUTHOR HERE
    """
    remove a pin from a comment. Take the following format.
    {
    "comment_id":str,
    "post_id":str
    }
    """
    
    if not current_user:
        raise HTTPException("401","Unauthorized")

    driver.remove_pinned_comment(comment_id, post_id)

@app.get("/api/posts")
async def get_all_posts(current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Pagination for all posts to replace feed. Currently just returns all posts from all users, no curated algo. 
    """
    # skip: int | None = Query(default=None), limit: int | None = Query(default=None)
    if current_user:
        feed = driver.get_feed(current_user, 0, 100)
        return(JSONResponse(content={"data": jsonable_encoder(feed)}))
    
@app.put("/api/review/{comment_id}/delete")
async def set_comment_as_deleted(comment_id:str, current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Set the deleted field for a comment and all replies to true
    """
    if not current_user:
        raise HTTPException("401","Unauthorized")
   
    if comment_id:
        driver.set_comment_as_deleted(comment_id)

@app.put("/api/review/{post_id}/delete")
async def set_post_as_deleted(post_id:str, current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Set the deleted field for a post and all comments to true
    """
    if not current_user:
        raise HTTPException("401","Unauthorized")
   
    if post_id:
        driver.set_post_as_deleted(post_id)

@app.get("/api/review/{post_id}/pinned_comments")
async def get_pinned_comments_for_post(post_id: str, current_user: Annotated[User, Depends(get_current_active_user)], skip: int | None = Query(default=None), limit: int | None = Query(default=None)):
    """
    Gets the pinned comments on a post
    Uses skip and limit for pagination
    """
    if not current_user:
        raise HTTPException("401","Unauthorized")
    if post_id:
        comments = driver.get_all_pinned_comments_for_post(post_id=post_id,
                                                    username=current_user.username,
                                                    skip=skip,
                                                    limit=limit)
        
        return JSONResponse(content={"data": jsonable_encoder(comments)})
    
@app.get("/api/books/{book_id}/versions")
async def get_book_versions_from_db(book_id: str):
    """
    Endpoint for getting versions of a book from the DB
    """
    if book_id[0] == "g":
        versions = driver.get_book_versions_by_google_id(book_id=book_id)
    else:
        versions = driver.get_book_versions(book_id=book_id)
    
    return JSONResponse(content={"data": jsonable_encoder(versions)})
        
@app.get("/api/books/{book_id}/versions/metadata")
async def get_book_versions_from_metadata_search(book_id: str, book_title:str, book_authors:list):
    """
    Endpoint for getting versions of a book from a metadata search
    """
    
    versions = search_versions_by_metadata(book_title=book_title,book_authors=book_authors)
    
    return JSONResponse(content={"data": jsonable_encoder(versions)})

