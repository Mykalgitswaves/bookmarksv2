import fastapi
from fastapi import HTTPException, Depends, BackgroundTasks, Request, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated

from src.api.utils.database import get_repository
from src.models.schemas.users import User
from src.models.schemas.posts import ReviewCreate, UpdateCreate, ComparisonCreate, RecommendationFriendCreate, MilestoneCreate
from src.models.schemas.comments import Comment, CommentCreate
from src.models.schemas.books import BookPreview
from src.securities.authorizations.verify import get_current_active_user
from src.database.graph.crud.posts import PostCRUDRepositoryGraph
from src.database.graph.crud.books import BookCRUDRepositoryGraph
from src.database.graph.crud.comments import CommentCRUDRepositoryGraph
from src.api.background_tasks.google_books import google_books_background_tasks


router = fastapi.APIRouter(prefix="/posts", tags=["post"])

@router.post("/create_review",
            name="post:create_review")
async def create_review(request: Request, 
                        current_user: Annotated[User, Depends(get_current_active_user)],
                        background_tasks: BackgroundTasks,
                        book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph)),
                        post_repo: PostCRUDRepositoryGraph = Depends(get_repository(repo_type=PostCRUDRepositoryGraph))):
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
        raise HTTPException(401,"Unauthorized")

    response = await request.json()
    if "_value" in response:
        response = response['_value']

    book_id = response['book_id']
    small_img_url = response['small_img_url']
    title = response['title']

    db_book = BookPreview(id=book_id, 
                          title=title, 
                          small_img_url=small_img_url)
    
    if book_id[0] == "g":
        canonical_book = book_repo.get_canonical_book_by_google_id(book_id) 
        if canonical_book:
            db_book = canonical_book


    review = ReviewCreate(
                    book=db_book,
                    user_username=current_user.username,
                    headline=response['headline'],
                    questions=response['questions'],
                    question_ids=response['ids'],
                    responses=response['responses'],
                    spoilers=response['spoilers']
            )
    review = post_repo.create_review(review)

    if db_book.id[0] == "g":
        background_tasks.add_task(google_books_background_tasks.update_book_google_id,db_book.id,book_repo)

    return JSONResponse(content={"data": jsonable_encoder(review)})

@router.post("/create_update",
            name="post:create_update")
async def create_update(request: Request, 
                        current_user: Annotated[User, Depends(get_current_active_user)],
                        background_tasks: BackgroundTasks,
                        book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph)),
                        post_repo: PostCRUDRepositoryGraph = Depends(get_repository(repo_type=PostCRUDRepositoryGraph))):
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
        raise HTTPException(401,"Unauthorized")

    response = await request.json()
    if "_value" in response:
        response = response['_value']

    book_id = response['book_id']
    small_img_url = response['small_img_url']
    title = response['title']

    db_book = BookPreview(id=book_id, 
                          title=title, 
                          small_img_url=small_img_url)
    
    if book_id[0] == "g":
        canonical_book = book_repo.get_canonical_book_by_google_id(book_id) 
        if canonical_book:
            db_book = canonical_book
        
    update = UpdateCreate(
                        book=db_book,
                        user_username=current_user.username,
                        headline=response['headline'],
                        page=response['page'],
                        response=response['response'],
                        spoiler=response['is_spoiler'])
    
    update = post_repo.create_update(update)

    if db_book.id[0] == "g":
        background_tasks.add_task(google_books_background_tasks.update_book_google_id,db_book.id,book_repo)

    return JSONResponse(content={"data": jsonable_encoder(update)})

@router.post("/create_comparison",
            name="post:create_comparison")
async def create_comparison(request: Request, 
                        current_user: Annotated[User, Depends(get_current_active_user)],
                        background_tasks: BackgroundTasks,
                        book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph)),
                        post_repo: PostCRUDRepositoryGraph = Depends(get_repository(repo_type=PostCRUDRepositoryGraph))):
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
        raise HTTPException(401,"Unauthorized")

    response = await request.json()
    if "_value" in response:
        response = response['_value']

    if response["book_ids"][0] == response["book_ids"][1]:
        raise HTTPException(400,"Comparisons require two unique books, please select another book for your post.")
    
    books = []
    
    books_metadata = zip(response['book_ids'],response['book_small_imgs'],response['book_titles'])

    for book_id, small_img_url, title in books_metadata:
        canonical_book = book_repo.get_canonical_book_by_google_id(book_id) 
        if canonical_book:
            db_book = canonical_book
        
        if db_book:
            books.append(db_book)
        else:
            books.append(BookPreview(id=book_id, 
                          title=title, 
                          small_img_url=small_img_url)
            )
            

    comparison = ComparisonCreate(
                                compared_books=books,
                                user_username=current_user.username,
                                comparators=response['comparator_topics'],
                                comparator_ids=response['comparator_ids'],
                                responses=response['responses'],
                                book_specific_headlines=response['book_specific_headlines'])
    
    comparison = post_repo.create_comparison(comparison)

    for book in books:
        if book.id == "g":
            background_tasks.add_task(google_books_background_tasks.update_book_google_id,book.id,book_repo)

    return JSONResponse(content={"data": jsonable_encoder(comparison)})

@router.post("/create_recommendation_friend",
            name="post:create_recommendation_friend")
async def create_recommendation_friend(request: Request, 
                                        current_user: Annotated[User, Depends(get_current_active_user)],
                                        background_tasks: BackgroundTasks,
                                        book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph)),
                                        post_repo: PostCRUDRepositoryGraph = Depends(get_repository(repo_type=PostCRUDRepositoryGraph))):
    """
    Creates a post of type RecommendationFriend
    
    {"book_id":,
     "to_user_username":,
     "from_user_text":,
     "to_user_text":
     }
    """
    if not current_user:
        raise HTTPException(401,"Unauthorized")

    response = await request.json()
    if "_value" in response:
        response = response['_value']

    book_id = response['book_id']
    small_img_url = response['small_img_url']
    title = response['title']

    db_book = BookPreview(id=book_id, 
                          title=title, 
                          small_img_url=small_img_url)
    
    if book_id[0] == "g":
        canonical_book = book_repo.get_canonical_book_by_google_id(book_id) 
        if canonical_book:
            db_book = canonical_book

    recommendation = RecommendationFriendCreate(
                                          book=db_book,
                                          user_username=current_user.username,
                                          to_user_username=response['to_user_username'],
                                          from_user_text=response['from_user_text'],
                                          to_user_text=response['to_user_text'],
                                          )
    
    recommendation = post_repo.create_recommendation_post(recommendation)

    if db_book.id[0] == "g":
        background_tasks.add_task(google_books_background_tasks.update_book_google_id,db_book.id,book_repo)

    return JSONResponse(content={"data": jsonable_encoder(recommendation)})

@router.post("/create_milestone",
            name="post:create_milestone")
async def create_milestone(request: Request, 
                            current_user: Annotated[User, Depends(get_current_active_user)],
                            post_repo: PostCRUDRepositoryGraph = Depends(get_repository(repo_type=PostCRUDRepositoryGraph))):
    """
    Creates a post of type Milestone
    
    {"num_books":
     }
    """
    if not current_user:
        raise HTTPException(401,"Unauthorized")

    response = await request.json()
    if "_value" in response:
        response = response['_value']
    
    milestone = MilestoneCreate(
                              user_username=current_user.username,
                              num_books=response['num_books'])
    
    milestone = post_repo.create_milestone(milestone)

    return JSONResponse(content={"data": jsonable_encoder(milestone)})

@router.put("/{post_id}/delete",
            name="post:delete")
async def update_post_to_deleted(post_id: str, 
                                 current_user: Annotated[User, Depends(get_current_active_user)],
                                 post_repo: PostCRUDRepositoryGraph = Depends(get_repository(repo_type=PostCRUDRepositoryGraph))):
    """
    Set the deleted field for a post and all comments to true
    """
    if not current_user:
        raise HTTPException(401,"Unauthorized")
   
    if post_id:
        response = post_repo.update_post_to_deleted(post_id, current_user.username)
        
        if response:
            return HTTPException(200,"Post deleted")
        else:
            raise HTTPException(401,"Unauthorized")
        
@router.get("/me",
            name="post:get_current_user_posts")
async def get_current_user_posts(current_user: Annotated[User, Depends(get_current_active_user)],
                                 post_repo: PostCRUDRepositoryGraph = Depends(get_repository(repo_type=PostCRUDRepositoryGraph))):
    if current_user:
        return(JSONResponse(content={"data": jsonable_encoder(post_repo.get_all_reviews_by_username(current_user.username))}))

@router.get("/{user_id}",
            name="post:get_user_posts")
async def get_user_posts(user_id:str,
                         current_user: Annotated[User, Depends(get_current_active_user)],
                         post_repo: PostCRUDRepositoryGraph = Depends(get_repository(repo_type=PostCRUDRepositoryGraph))):
    if current_user:
        return(JSONResponse(content={"data": jsonable_encoder(post_repo.get_all_reviews_by_user_id(user_id))}))
    
@router.get("/post/{post_id}",
            name="post:get_post")
async def get_post(post_id: str, 
                   current_user: Annotated[User, Depends(get_current_active_user)],
                   post_repo: PostCRUDRepositoryGraph = Depends(get_repository(repo_type=PostCRUDRepositoryGraph))):
    if post_id and current_user:
        data = post_repo.get_post(post_id=post_id, username=current_user.username)
        if data:
            post = data["post"]
            user_id = data["user_id"]
            post_type = type(post).__name__
            return (JSONResponse(content={"data": jsonable_encoder({"post": post, "post_type": post_type, "op_user_id": user_id})}))
        else:
            raise HTTPException("404","Post not found")
        
@router.post("/comment/create",
            name="post:create_comment")
async def create_comment(request: Request, 
                         current_user: Annotated[User, Depends(get_current_active_user)],
                         comment_repo: CommentCRUDRepositoryGraph = Depends(get_repository(repo_type=CommentCRUDRepositoryGraph))):
    """
    Endpoint for posting a comment.

    Value 'replied_to' should be None if comment is not a reply to another comment
    """
    if not current_user:
        raise HTTPException(401,"Unauthorized")

    response = await request.json()

    comment = CommentCreate(
                            post_id=response['post_id'],
                            username=current_user.username,
                            replied_to=response['replied_to'],
                            text=response['text'])
    
    comment = comment_repo.create_comment(comment)

    if not comment:
        raise HTTPException(410," Gone - This chapter closes, yet its essence endures beyond the veil")
    
    comment.posted_by_current_user = True

    return JSONResponse(content={"data": jsonable_encoder(comment)})

@router.put("/comment/{comment_id}/delete",
            name="post:delete_comment")
async def set_comment_as_deleted(comment_id:str, 
                                 current_user: Annotated[User, Depends(get_current_active_user)],
                                 comment_repo: CommentCRUDRepositoryGraph = Depends(get_repository(repo_type=CommentCRUDRepositoryGraph))):
    """
    Set the deleted field for a comment and all replies to true
    """
    if not current_user:
        raise HTTPException(401,"Unauthorized")
   
    if comment_id:
        response = comment_repo.update_comment_to_deleted(comment_id, current_user.username)

        if response:
            return HTTPException(200,"Post deleted")
        else:
            raise HTTPException(401,"Unauthorized")


@router.get("/post/{post_id}/comments")
async def get_comments_for_post(post_id: str, 
                                current_user: Annotated[User, Depends(get_current_active_user)],
                                comment_repo: CommentCRUDRepositoryGraph = Depends(get_repository(repo_type=CommentCRUDRepositoryGraph)), 
                                skip: int = Query(default=0), 
                                limit: int = Query(default=10)):
    """
    Gets the comments on a post
    Uses skip and limit for pagination
    """
    if not current_user:
        raise HTTPException(401,"Unauthorized")
    if post_id:
        comments = comment_repo.get_all_comments_for_post(post_id=post_id,
                                                    username=current_user.username,
                                                    skip=skip,
                                                    limit=limit)
  
        return JSONResponse(content={"data": jsonable_encoder({"comments": comments['comments'], "pinned_comments": comments['pinned_comments']})})
