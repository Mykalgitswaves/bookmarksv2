import fastapi
from fastapi import Depends, HTTPException, Request

from src.database.sql.crud.users import UserRepository
from src.database.sql.models.users import UserTest

from src.database.graph.crud.users import UserCRUDRepositoryGraph
from src.database.graph.crud.books import BookCRUDRepositoryGraph
from src.database.graph.crud.posts import PostCRUDRepositoryGraph
from src.database.graph.crud.bookclubs import BookClubCRUDRepositoryGraph
from src.api.utils.database import get_repository, get_sql_repository
from src.config.config import settings
from src.utils.logging.logger import logger

router = fastapi.APIRouter(prefix="/admin", tags=["admin"])


@router.post("/delete_user_by_username", name="admin:delete_user_by_username")
async def delete_user_by_username(
    request: Request,
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    logger.warning("Admin is deleting a user by username")
    data = await request.json()

    username = data.get("username")
    admin_credentials = data.get("admin_credentials")

    if admin_credentials != settings.ADMIN_CREDENTIALS:
        raise HTTPException(status_code=403, detail="Forbidden")
    else:
        response = user_repo.delete_user_by_username(username)
        if response:
            logger.warning("Admin has deleted a user by username", extra={"username": username})
            return HTTPException(status_code=200, detail="User deleted")
        else:
            return HTTPException(status_code=404, detail="User not found")


@router.post(
    "/delete_book_and_versions_by_google_id",
    name="admin:delete_book_and_versions_by_google_id",
)
async def delete_book_and_versions_by_google_id(
    request: Request,
    book_repo: BookCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookCRUDRepositoryGraph)
    ),
):
    logger.warning("Admin is deleting a book and its versions by google id")
    data = await request.json()

    google_id = data.get("google_id")
    admin_credentials = data.get("admin_credentials")

    if admin_credentials != settings.ADMIN_CREDENTIALS:
        raise HTTPException(status_code=403, detail="Forbidden")
    else:
        response = book_repo.delete_book_and_versions_by_google_id(google_id)
        if response:
            logger.warning("Admin has deleted a book and its versions by google id")
            return HTTPException(status_code=200, detail="Book deleted")
        else:
            return HTTPException(status_code=404, detail="Book not found")


@router.post("/delete_post_and_comments", name="admin:delete_post_and_comments")
async def delete_post_and_comments(
    request: Request,
    post_repo: PostCRUDRepositoryGraph = Depends(
        get_repository(repo_type=PostCRUDRepositoryGraph)
    ),
):
    logger.warning("Admin is deleting a post and its comments")
    data = await request.json()

    post_id = data.get("post_id")
    admin_credentials = data.get("admin_credentials")

    if admin_credentials != settings.ADMIN_CREDENTIALS:
        raise HTTPException(status_code=403, detail="Forbidden")
    else:
        response = post_repo.delete_post(post_id)
        if response:
            logger.warning("Admin has deleted a post and its comments")
            return HTTPException(status_code=200, detail="Post deleted")
        else:
            return HTTPException(status_code=404, detail="Post not found")


@router.post("/create_user_sql", name="admin:create_user_sql")
async def create_user_sql(
    request: Request,
    user_repo: UserRepository = Depends(get_sql_repository(repo_type=UserRepository)),
):
    data = await request.json()

    admin_credentials = data.get("admin_credentials")

    if admin_credentials != settings.ADMIN_CREDENTIALS:
        raise HTTPException(status_code=403, detail="Forbidden")

    user = UserTest(
        username=data.get("username"),
        email=data.get("email"),
        full_name=data.get("full_name"),
        user_id=data.get("user_id"),
    )

    response = await user_repo.create_user(user)

    return response


@router.get("/get_user_sql", name="admin:get_user_sql")
async def get_user_sql(
    request: Request,
    user_repo: UserRepository = Depends(get_sql_repository(repo_type=UserRepository)),
):
    data = await request.json()

    user_id = data.get("user_id")

    response = await user_repo.get_user(user_id)

    return response


@router.delete("/delete_user_sql", name="admin:delete_user_sql")
async def delete_user_sql(
    request: Request,
    user_repo: UserRepository = Depends(get_sql_repository(repo_type=UserRepository)),
):
    data = await request.json()

    user_id = data.get("user_id")

    response = await user_repo.delete_user(user_id)

    return response


@router.post("/delete_user_book_club_data", name="admin:delete_club")
async def delete_user_book_club_data(
    request: Request,
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
):
    """
    Deletes a users book club data, including all book club books, book clubs,
    and paces.

    Args:
        request: a request object that contains:
            admin_credentials: the admin credentials for the user
            user_id: the user
    """
    logger.warning("Admin is deleting a user's book club data")
    data = await request.json()

    user_id = data.get("user_id")
    admin_credentials = data.get("admin_credentials")

    if admin_credentials != settings.ADMIN_CREDENTIALS:
        raise HTTPException(status_code=403, detail="Forbidden")
    else:
        response = book_club_repo.delete_book_club_data(user_id)
        if response:
            logger.warning("Admin has deleted a user's book club data")
            return HTTPException(status_code=200, detail="Post deleted")
        else:
            return HTTPException(status_code=404, detail="Post not found")
