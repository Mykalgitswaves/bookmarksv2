import fastapi
from fastapi import HTTPException, Depends, BackgroundTasks, Request, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated, Optional

from src.api.utils.database import get_repository
from src.models.schemas.users import User
from src.models.schemas.posts import (
    ReviewCreate,
    UpdateCreate,
    ComparisonCreate,
    RecommendationFriendCreate,
    MilestoneCreate,
    LikedPost,
)
from src.models.schemas.comments import (
    Comment,
    CommentCreate,
    LikedComment,
    PinnedComment,
)
from src.models.schemas.books import BookPreview
from src.securities.authorizations.verify import get_current_active_user
from src.database.graph.crud.posts import PostCRUDRepositoryGraph
from src.database.graph.crud.books import BookCRUDRepositoryGraph
from src.database.graph.crud.comments import CommentCRUDRepositoryGraph
from src.api.background_tasks.google_books import google_books_background_tasks
from src.utils.logging.logger import logger

router = fastapi.APIRouter(prefix="/posts", tags=["post"])


@router.get("/", name="post:get_all_posts")
async def get_all_posts(
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = Query(default=0),
    limit: int = Query(default=10),
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
    """
    Pagination for all posts to replace feed. Currently just returns all posts from all users, no curated algo.
    """
    # skip: int | None = Query(default=None), limit: int | None = Query(default=None)
    if current_user:
        feed = post_repo.get_feed(current_user, skip, limit)
        logger.info(
            "Retrieved feed for User",
            extra={
                "user_id": current_user.id,
                "action": "get_feed"
            }
        )
        return JSONResponse(content={"data": jsonable_encoder(feed)})


@router.post("/create_review", name="post:create_review")
async def create_review(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    background_tasks: BackgroundTasks,
    book_repo: BookCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookCRUDRepositoryGraph)
    ),
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
    """
    Creates a post of type Review

    {"book_id":,
     "headline":,
     questions:[]
     ids:[]
     responses:[]
     spoilers:[]
     rating: int | None = None
     }

    """
    if not current_user:
        raise HTTPException(401, "Unauthorized")

    response = await request.json()
    if "_value" in response:
        response = response["_value"]

    book_id = response["book_id"]
    small_img_url = response["small_img_url"]
    title = response["title"]

    try:
        db_book = BookPreview(id=book_id, title=title, small_img_url=small_img_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

    book_exists = True
    if book_id[0] == "g":
        book_exists = False
        canonical_book = book_repo.get_canonical_book_by_google_id(book_id)
        if canonical_book:
            book_exists = True
            db_book = canonical_book

    try:
        review = ReviewCreate(
            book=db_book,
            user_username=current_user.username,
            headline=response["headline"],
            questions=response["questions"],
            question_ids=response["ids"],
            responses=response["responses"],
            spoilers=response["spoilers"],
            rating=response.get("rating"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

    if book_exists:
        review = post_repo.create_review(review)
    else:
        review = post_repo.create_review_and_book(review)

    if not book_exists:
        print("triggering background task")
        background_tasks.add_task(
            google_books_background_tasks.update_book_google_id,
            review.book.google_id,
            book_repo,
        )

    logger.info(
        "Created Review",
        extra={
            "user_id": current_user.id,
            "book_id": review.book.id,
            "action": "create_review"
        }
    )
    return JSONResponse(content={"data": jsonable_encoder(review)})


@router.post("/create_update", name="post:create_update")
async def create_update(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    background_tasks: BackgroundTasks,
    book_repo: BookCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookCRUDRepositoryGraph)
    ),
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
    """
    Creates a post of type Update

    {"book_id":,
     "headline":,
     "page",
     questions:[]
     ids:[]
     responses:[]
     spoilers:[],
     quote
     }

    """
    if not current_user:
        raise HTTPException(401, "Unauthorized")

    response = await request.json()
    if "_value" in response:
        response = response["_value"]

    book_id = response["book_id"]
    small_img_url = response["small_img_url"]
    title = response["title"]

    try:
        db_book = BookPreview(id=book_id, title=title, small_img_url=small_img_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

    book_exists = True
    if book_id[0] == "g":
        book_exists = False
        canonical_book = book_repo.get_canonical_book_by_google_id(book_id)
        if canonical_book:
            book_exists = True
            db_book = canonical_book

    try:
        update = UpdateCreate(
            book=db_book,
            user_username=current_user.username,
            headline=response.get("headline"),
            page=response.get("page"),
            chapter=response.get('chapter'),
            response=response.get("response"),
            spoiler=response.get("is_spoiler"),
            quote=response.get("quote"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

    if book_exists:
        update = post_repo.create_update(update)
    else:
        update = post_repo.create_update_and_book(update)

    if not book_exists:
        background_tasks.add_task(
            google_books_background_tasks.update_book_google_id,
            update.book.google_id,
            book_repo,
        )

    logger.info(
        "Created Update",
        extra={
            "user_id": current_user.id,
            "book_id": update.book.id,
            "action": "create_update"
        }
    )
    return JSONResponse(content={"data": jsonable_encoder(update)})


@router.post("/create_comparison", name="post:create_comparison")
async def create_comparison(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    background_tasks: BackgroundTasks,
    book_repo: BookCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookCRUDRepositoryGraph)
    ),
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
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
        raise HTTPException(401, "Unauthorized")

    response = await request.json()
    if "_value" in response:
        response = response["_value"]

    if response["book_ids"][0] == response["book_ids"][1]:
        logger.warning(
            "Attempted to create comparison between the same book",
            extra={
                "user_id": current_user.id,
                "book_1_id": response["book_ids"][0],
                "book_2_id": response["book_ids"][1]
            }
        )
        raise HTTPException(
            400,
            "Comparisons require two unique books, please select another book for your post.",
        )

    books = []

    books_metadata = zip(
        response["book_ids"], response["book_small_imgs"], response["book_titles"]
    )

    all_books_exist = True
    for book_id, small_img_url, title in books_metadata:
        canonical_book = book_repo.get_canonical_book_by_google_id(book_id)

        if canonical_book:
            books.append(canonical_book)
        else:
            all_books_exist = False
            try:
                if book_id[0] == "g":
                    books.append(
                        BookPreview(
                            id=book_id,
                            title=title,
                            small_img_url=small_img_url,
                            google_id=book_id,
                        )
                    )
                else:
                    raise ValueError("Book does not exist in the database")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

    try:
        comparison = ComparisonCreate(
            compared_books=books,
            user_username=current_user.username,
            comparators=response["comparator_topics"],
            comparator_ids=response["comparator_ids"],
            responses=response["responses"],
            book_specific_headlines=response["book_specific_headlines"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

    if all_books_exist:
        comparison = post_repo.create_comparison(comparison)
    else:
        comparison = post_repo.create_comparison_and_books(comparison)

    for book in books:
        if book.id == "g":
            background_tasks.add_task(
                google_books_background_tasks.update_book_google_id,
                book.google_id,
                book_repo,
            )

    logger.info(
        "Created Comparison",
        extra={
            "user_id": current_user.id,
            "book_1_id": response["book_ids"][0],
            "book_2_id": response["book_ids"][1],
            "action": "create_comparison"
        }
    )
    return JSONResponse(content={"data": jsonable_encoder(comparison)})


@router.post("/create_recommendation_friend", name="post:create_recommendation_friend")
async def create_recommendation_friend(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    background_tasks: BackgroundTasks,
    book_repo: BookCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookCRUDRepositoryGraph)
    ),
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
    """
    Creates a post of type RecommendationFriend

    {"book_id":,
     "to_user_username":,
     "from_user_text":,
     "to_user_text":
     }
    """
    if not current_user:
        raise HTTPException(401, "Unauthorized")

    response = await request.json()
    if "_value" in response:
        response = response["_value"]

    book_id = response["book_id"]
    small_img_url = response["small_img_url"]
    title = response["title"]

    try:
        db_book = BookPreview(id=book_id, title=title, small_img_url=small_img_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

    book_exists = True
    if book_id[0] == "g":
        book_exists = False
        canonical_book = book_repo.get_canonical_book_by_google_id(book_id)
        if canonical_book:
            book_exists = True
            db_book = canonical_book

    try:
        recommendation = RecommendationFriendCreate(
            book=db_book,
            user_username=current_user.username,
            to_user_username=response["to_user_username"],
            from_user_text=response["from_user_text"],
            to_user_text=response["to_user_text"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

    if book_exists:
        recommendation = post_repo.create_recommendation_post(recommendation)
    else:
        recommendation = post_repo.create_recommendation_post_and_book(recommendation)

    if not book_exists:
        background_tasks.add_task(
            google_books_background_tasks.update_book_google_id,
            recommendation.book.google_id,
            book_repo,
        )

    logger.info(
        "Created Recommendation",
        extra={
            "user_id": current_user.id,
            "to_user_username": response["to_user_username"],
            "book_id": recommendation.book.id,
            "action": "create_recommendation"
        }
    )
    return JSONResponse(content={"data": jsonable_encoder(recommendation)})


@router.post("/create_milestone", name="post:create_milestone")
async def create_milestone(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
    """
    Creates a post of type Milestone

    {"num_books":
     }
    """
    if not current_user:
        raise HTTPException(401, "Unauthorized")

    response = await request.json()
    if "_value" in response:
        response = response["_value"]

    try:
        milestone = MilestoneCreate(
            user_username=current_user.username, num_books=response["num_books"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

    milestone = post_repo.create_milestone(milestone)

    logger.info(
        "Created Milestone",
        extra={
            "user_id": current_user.id,
            "num_books": response["num_books"],
            "action": "create_milestone"
        }
    )
    return JSONResponse(content={"data": jsonable_encoder(milestone)})


@router.delete("/post/{post_id}/delete", name="post:delete")
async def update_post_to_deleted(
    post_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
    """
    Set the deleted field for a post and all comments to true
    """
    if not current_user:
        raise HTTPException(401, "Unauthorized")

    if post_id:
        response = post_repo.update_post_to_deleted(post_id, current_user.username)

        if response:
            logger.info(
                "Deleted Post",
                extra={
                    "user_id": current_user.id,
                    "post_id": post_id,
                    "action": "delete_post"
                }
            )
            return HTTPException(200, "Post deleted")
        else:
            logger.warning(
                "Failed to delete a post",
                extra={
                    "user_id": current_user.id,
                    "post_id": post_id,
                    "action": "delete_post"
                }
            )
            raise HTTPException(401, "Unauthorized")


@router.put("/post/{post_id}/like", name="post:like")
async def like_post(
    post_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
    """
    Adds a like to a post. Take the following format.
    """
    try:
        liked_post = LikedPost(username=current_user.username, post_id=post_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

    if not current_user:
        raise HTTPException(401, "Unauthorized")

    if post_id:
        response = post_repo.create_post_like(liked_post)
        if response:
            return HTTPException(200, "Post liked")
        else:
            raise HTTPException(401, "Unauthorized")


@router.put("/post/{post_id}/remove_like", name="post:remove_like")
async def remove_like_post(
    post_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
    """
    remove a like to a post.
    """
    try:
        liked_post = LikedPost(username=current_user.username, post_id=post_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not current_user:
        raise HTTPException(401, "Unauthorized")

    if post_id:
        response = post_repo.delete_post_like(liked_post)
        if response:
            return HTTPException(200, "Post like removed")
        else:
            raise HTTPException(401, "Unauthorized")


@router.get("/me", name="post:get_current_user_posts")
async def get_current_user_posts(
    current_user: Annotated[User, Depends(get_current_active_user)],
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
    if current_user:
        logger.info(
            "Retrieved posts for current user",
            extra={
                "user_id": current_user.id,
                "action": "get_posts_for_current_user"
            }
        )
        return JSONResponse(
            content={
                "data": jsonable_encoder(
                    post_repo.get_all_reviews_by_username(current_user.username)
                )
            }
        )


@router.get("/{user_id}", name="post:get_user_posts")
async def get_user_posts(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
    if current_user:
        logger.info(
            "Retrieved posts for specific user",
            extra={
                "user_id": current_user.id,
                "action": "get_posts_for_specific_user"
            }
        )
        return JSONResponse(
            content={
                "data": jsonable_encoder(post_repo.get_all_reviews_by_user_id(user_id))
            }
        )


@router.get("/post/{post_id}", name="post:get_post")
async def get_post(
    post_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
    """
    Get a specific post by id
    """
    if post_id and current_user:
        data = post_repo.get_post(post_id=post_id, username=current_user.username)
        if data:
            post = data["post"]
            user_id = data["user_id"]
            post_type = type(post).__name__
            logger.info(
                "Retrieved post by id",
                extra={
                    "user_id": current_user.id,
                    "post_id": post_id,
                    "action": "get_post_by_id"
                }
            )
            return JSONResponse(
                content={
                    "data": jsonable_encoder(
                        {"post": post, "post_type": post_type, "op_user_id": user_id}
                    )
                }
            )
        else:
            logger.warning(
                "Failed to retrieve post by id",
                extra={
                    "user_id": current_user.id,
                    "post_id": post_id,
                    "action": "get_post_by_id"
                }
            )
            raise HTTPException("404", "Post not found")


@router.post("/comment/create", name="post:create_comment")
async def create_comment(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    comment_repo: CommentCRUDRepositoryGraph = Depends(
        get_repository(repo_type=CommentCRUDRepositoryGraph)
    ),
):
    """
    Endpoint for posting a comment.

    Value 'replied_to' should be None if comment is not a reply to another comment
    """
    if not current_user:
        raise HTTPException(401, "Unauthorized")

    response = await request.json()

    try:
        comment = CommentCreate(
            post_id=response["post_id"],
            username=current_user.username,
            replied_to=response["replied_to"],
            text=response["text"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))
    
    if comment.post_id.startswith("club_"):
        comment = comment_repo.create_comment_for_club(comment)
    else:
        comment = comment_repo.create_comment(comment)

    if not comment:
        logger.warning(
            "Failed to create comment",
            extra={
                "user_id": current_user.id,
                "post_id": response["post_id"],
                "comment_text": response["text"],
                "action": "create_comment"
            }
        )
        raise HTTPException(
            410, " Gone - This chapter closes, yet its essence endures beyond the veil"
        )

    comment.posted_by_current_user = True

    logger.info(
        "Created Comment",
        extra={
            "user_id": current_user.id,
            "post_id": response["post_id"],
            "comment_text": response["text"],
            "action": "create_comment"
        }
    )

    return JSONResponse(content={"data": jsonable_encoder(comment)})


@router.put("/comment/{comment_id}/delete", name="post:delete_comment")
async def set_comment_as_deleted(
    comment_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    comment_repo: CommentCRUDRepositoryGraph = Depends(
        get_repository(repo_type=CommentCRUDRepositoryGraph)
    ),
):
    """
    Set the deleted field for a comment and all replies to true
    """
    if not current_user:
        raise HTTPException(401, "Unauthorized")

    if comment_id:
        response = comment_repo.update_comment_to_deleted(
            comment_id, current_user.username
        )

        if response:
            logger.info(
                "Deleted Comment",
                extra={
                    "user_id": current_user.id,
                    "comment_id": comment_id,
                    "action": "delete_comment"
                }
            )
            return HTTPException(200, "Comment deleted")
        else:
            logger.warning(
                "Failed to delete comment",
                extra={
                    "user_id": current_user.id,
                    "comment_id": comment_id,
                    "action": "delete_comment"
                }
            )
            raise HTTPException(401, "Unauthorized")


@router.put("/comment/{comment_id}/like", name="comment:like")
async def like_comment(
    comment_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    comment_repo: CommentCRUDRepositoryGraph = Depends(
        get_repository(repo_type=CommentCRUDRepositoryGraph)
    ),
):
    """
    Adds a like to a Comment.
    """

    try:
        liked_comment = LikedComment(
            username=current_user.username, comment_id=comment_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not current_user:
        raise HTTPException(401, "Unauthorized")

    if comment_id:
        response = comment_repo.create_comment_like(liked_comment)
        if response:
            return HTTPException(200, "Post liked")
        else:
            raise HTTPException(401, "Unauthorized")


@router.put("/comment/{comment_id}/remove_like", name="comment:remove_like")
async def remove_like_comment(
    comment_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    comment_repo: CommentCRUDRepositoryGraph = Depends(
        get_repository(repo_type=CommentCRUDRepositoryGraph)
    ),
):
    """
    remove a like to a comment.
    """
    try:
        liked_comment = LikedComment(
            username=current_user.username, comment_id=comment_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not current_user:
        raise HTTPException(401, "Unauthorized")

    if comment_id:
        response = comment_repo.delete_comment_like(liked_comment)
        if response:
            return HTTPException(200, "Post like removed")
        else:
            raise HTTPException(401, "Unauthorized")


@router.get("/post/{post_id}/pinned_comments", name="post:get_pinned_comments")
async def get_pinned_comments_for_post(
    post_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = Query(default=0),
    limit: int = Query(default=10),
    comment_repo: CommentCRUDRepositoryGraph = Depends(
        get_repository(repo_type=CommentCRUDRepositoryGraph)
    ),
):
    """
    Gets the pinned comments on a post
    Uses skip and limit for pagination
    """
    if not current_user:
        raise HTTPException("401", "Unauthorized")

    if post_id:
        comments = comment_repo.get_all_pinned_comments_for_post(
            post_id=post_id, username=current_user.username, skip=skip, limit=limit
        )
        logger.info(
            "Retrieved pinned comments for post",
            extra={
                "user_id": current_user.id,
                "post_id": post_id,
                "num_pinned_comments": len(comments),
                "action": "get_pinned_comments_for_post"
            }
        )
        return JSONResponse(content={"data": jsonable_encoder(comments)})


@router.put("/post/{post_id}/pin/{comment_id}", name="comment:pin")
async def pin_comment(
    comment_id: str,
    post_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    comment_repo: CommentCRUDRepositoryGraph = Depends(
        get_repository(repo_type=CommentCRUDRepositoryGraph)
    ),
):
    """
    Adds a pin to a comment. Take the following format.
    {
    "comment_id":str,
    "post_id":str
    }
    """
    if not current_user:
        raise HTTPException(401, "Unauthorized")

    try:
        pinned_comment = PinnedComment(
            username=current_user.username, comment_id=comment_id, post_id=post_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if pinned_comment:
        response = comment_repo.create_comment_pin(pinned_comment)

        if response:
            logger.info(
                "Pinned Comment",
                extra={
                    "user_id": current_user.id,
                    "comment_id": comment_id,
                    "post_id": post_id,
                    "action": "pin_comment"
                }
            )
            return HTTPException(200, "Comment pinned")
        else:
            logger.warning(
                "Failed to pin comment",
                extra={
                    "user_id": current_user.id,
                    "comment_id": comment_id,
                    "post_id": post_id,
                    "action": "pin_comment"
                }
            )
            raise HTTPException(401, "Unauthorized")


@router.put("/post/{post_id}/remove_pin/{comment_id}", name="comment:remove_pin")
async def remove_pin_comment(
    post_id: str,
    comment_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    comment_repo: CommentCRUDRepositoryGraph = Depends(
        get_repository(repo_type=CommentCRUDRepositoryGraph)
    ),
):
    """
    remove a pin from a comment. Take the following format.
    {
    "comment_id":str,
    "post_id":str
    }
    """

    if not current_user:
        raise HTTPException(401, "Unauthorized")

    try:
        pinned_comment = PinnedComment(
            username=current_user.username, comment_id=comment_id, post_id=post_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if pinned_comment:
        response = comment_repo.delete_comment_pin(pinned_comment)

        if response:
            logger.info(
                "Removed Comment Pin",
                extra={
                    "user_id": current_user.id,
                    "comment_id": comment_id,
                    "post_id": post_id,
                    "action": "remove_comment_pin"
                }
            )
            return HTTPException(200, "Comment pin removed")
        else:
            logger.warning(
                "Failed to remove comment pin",
                extra={
                    "user_id": current_user.id,
                    "comment_id": comment_id,
                    "post_id": post_id,
                    "action": "remove_comment_pin"
                }
            )
            raise HTTPException(401, "Unauthorized")


@router.get("/post/{post_id}/comments")
async def get_comments_for_post(
    post_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    comment_repo: CommentCRUDRepositoryGraph = Depends(
        get_repository(repo_type=CommentCRUDRepositoryGraph)
    ),
    skip: int = Query(default=0),
    limit: int = Query(default=10),
    book_club_id: Optional[str] = None,
    depth: int = 10 
):
    """
    Gets all the comments for a specific post, paginated by a skip and limit

    Args:
        post_id: The post to grab comments for
        current_user: The current user data
        comment_repo: The CRUD repo containing the comment queries
        skip: The skip value for level 0 comments
        limit: The limit value for level 0 comments
        book_club_id: OPTIONAL If post is from a bookclub, this is the bookclub id
        depth: The maximum depth to go in a thread

    Returns:
        comments (list): A list of unpinned comments
        pinned_comments (list): A list of pinned comments

    Here is the example format for one comment:
        {
        "id": comment_id,
        "user_id": comment author user id,
        ...
        "thread": list of the top liked replies for each level under level 0
            Comment data it the same in here as above
        }
    """
    if not current_user:
        raise HTTPException(401, "Unauthorized")
    
    if depth < 1 or depth > 20:
        raise HTTPException(
            status_code=400, 
            detail="Value for depth must be between 1 and 20"
            )
    
    if post_id:
        # Check that you are a member of a club before returning any comments. Slightly slower. 
        # TO_CONSIDER: Alternatively you could save a token to authenticate on the client 
        # what their permissions are to view comments. Would be way faster but would require a little bit of setup. 
        if book_club_id:
            comments = comment_repo.get_paginated_comments_for_book_club_post(
                post_id=post_id, 
                user_id=current_user.id, 
                skip=skip, 
                limit=limit, 
                book_club_id=book_club_id,
                depth=depth
            )

            return JSONResponse(
                content={
                    "data": jsonable_encoder(
                        {
                            "comments": comments["comments"],
                            "pinned_comments": comments["pinned_comments"],
                        }
                    )
                }
            )
        else:
            comments = comment_repo.get_all_comments_for_post(
                post_id=post_id, 
                user_id=current_user.id, 
                skip=skip, 
                limit=limit,
                depth=depth
            )

        return JSONResponse(
            content={
                "data": jsonable_encoder(
                    {
                        "comments": comments["comments"],
                        "pinned_comments": comments["pinned_comments"],
                    }
                )
            }
        )

@router.get("/post/{post_id}/comments/{comment_id}")
async def get_comments_for_comment(
    post_id: str,
    comment_id:str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    comment_repo: CommentCRUDRepositoryGraph = Depends(
        get_repository(repo_type=CommentCRUDRepositoryGraph)
    ),
    skip: int = Query(default=0),
    limit: int = Query(default=10),
    book_club_id: Optional[str] = None,
    depth: int = 10 
):
    """
    Gets all the comments for a specific post, paginated by a skip and limit

    Args:
        post_id: The post to grab comments for
        current_user: The current user data
        comment_repo: The CRUD repo containing the comment queries
        skip: The skip value for level 0 comments
        limit: The limit value for level 0 comments
        book_club_id: OPTIONAL If post is from a bookclub, this is the bookclub id
        depth: The maximum depth to go in a thread

    Returns:
        comments (list): A list of unpinned comments
        pinned_comments (list): A list of pinned comments

    Here is the example format for one comment:
        {
        "id": comment_id,
        "user_id": comment author user id,
        ...
        "thread": list of the top liked replies for each level under level 0
            Comment data it the same in here as above
        }
    """
    if not current_user:
        raise HTTPException(401, "Unauthorized")
    
    if depth < 1 or depth > 20:
        raise HTTPException(
            status_code=400, 
            detail="Value for depth must be between 1 and 20"
            )
    
    if post_id:
        # Check that you are a member of a club before returning any comments. Slightly slower. 
        # TO_CONSIDER: Alternatively you could save a token to authenticate on the client 
        # what their permissions are to view comments. Would be way faster but would require a little bit of setup. 
        if book_club_id:
            parent_comment = comment_repo.get_parent_comment_for_book_club(
                comment_id=comment_id,
                user_id=current_user.id, 
                book_club_id=book_club_id,
                post_id=post_id,
            )

            comments = comment_repo.get_paginated_comments_for_book_club_comment(
                post_id=post_id,
                comment_id=comment_id,
                user_id=current_user.id, 
                skip=skip, 
                limit=limit, 
                book_club_id=book_club_id,
                depth=depth
            )

            return JSONResponse(
                content={
                    "data": jsonable_encoder(
                        {
                            "parent_comment": parent_comment,
                            "comments": comments,
                        }
                    )
                }
            )
        else:
            comments = comment_repo.get_all_comments_for_comment(
                post_id=post_id,
                comment_id=comment_id,
                user_id=current_user.id, 
                skip=skip, 
                limit=limit,
                depth=depth
            )

        return JSONResponse(
            content={
                "data": jsonable_encoder(
                    {
                        "comments": comments
                    }
                )
            }
        )  

@router.get(
    "/comment/{comment_id}/replies", name="comment:get_replies"
)  # /api/posts/comments/{comment_id}/replies
async def get_all_replies_for_comment(
    comment_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    comment_repo: CommentCRUDRepositoryGraph = Depends(
        get_repository(repo_type=CommentCRUDRepositoryGraph)
    ),
):
    """
    Returns a list of comments for a specific reply.
    """
    if not current_user:
        raise HTTPException(401, "Unauthorized")
    if comment_id:
        replies = comment_repo.get_all_replies_for_comment(
            comment_id=comment_id, username=current_user.username
        )
        logger.info(
            "Retrieved replies for comment",
            extra={
                "user_id": current_user.id,
                "comment_id": comment_id,
                "num_replies": len(replies),
                "action": "get_replies_for_comment"
            }
        )
        return JSONResponse(content={"data": jsonable_encoder(replies)})
