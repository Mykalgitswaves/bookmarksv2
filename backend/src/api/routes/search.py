import fastapi
from fastapi import HTTPException, Depends, BackgroundTasks, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated, Optional

from src.api.utils.database import get_repository
from src.database.graph.crud.search import SearchCRUDRepositoryGraph
from src.models.schemas.search import SearchSchema
from src.models.schemas.users import User
from src.securities.authorizations.verify import get_current_active_user
from src.book_apis.google_books.search import google_books_search
from src.utils.logging.logger import logger

router = fastapi.APIRouter(prefix="/search", tags=["search"])


@router.get("/{param}", name="search:full")
def search_for_param(
    param: str,
    skip: int = 0,
    limit: int = 5,
    search_repo: SearchCRUDRepositoryGraph = Depends(
        get_repository(repo_type=SearchCRUDRepositoryGraph)
    ),
):
    """
    Endpoint used for searching for users, todo add in credentials for searching
    """

    books_result = google_books_search.search(param, skip, limit)
    search_result = search_repo.search_for_param(param=param, skip=skip, limit=limit)
    search_result["books"] = books_result
    logger.info(
        "Searched for param in repository",
        extra={
            "param": param,
            "action": "search_for_param",
        }
    )

    return JSONResponse(content={"data": jsonable_encoder(search_result)})


@router.get("/book/{param}", name="search:books")
def search_for_param_book(param: str, skip: int = 0, limit: int = 5):
    """
    Endpoint used for searching for users, todo add in credentials for searching
    """

    books_result = google_books_search.search(param, skip, limit)
    logger.info(
        "Search for param in google books",
        extra={
            "param": param,
            "action": "search_for_param_book",
        }
    )

    return JSONResponse(content={"data": jsonable_encoder(books_result)})


@router.get("/users/{param}", name="search:users")
def search_for_param_user(
    param: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 5,
    search_repo: SearchCRUDRepositoryGraph = Depends(
        get_repository(repo_type=SearchCRUDRepositoryGraph)
    ),
):
    """
    Endpoint used for searching for users, todo add in credentials for searching
    """

    search_result = search_repo.get_users_full_text_search(
        search_query=param, skip=skip, limit=limit, current_user_id=current_user.id
    )

    logger.info(
        "Searched for user by param",
        extra={
            "param": param,
            "user_id": current_user.id,
            "action": "search_for_param_user",
        }
    )

    return JSONResponse(content={"data": jsonable_encoder(search_result)})


@router.get("/friends/{param}", name="search:friends")
def search_for_param_friend(
    param: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 5,
    bookshelf_id: Optional[str] = Query(
        None,
        description="Used to exclude existing contributors and members for a bookshelf suggested friends list.",
    ),
    search_repo: SearchCRUDRepositoryGraph = Depends(
        get_repository(repo_type=SearchCRUDRepositoryGraph)
    ),
):
    """
    Endpoint used for searching for friends, todo add in credentials for searching
    """

    if bookshelf_id:
        search_result = search_repo.get_friends_full_text_search_no_bookshelf_access(
            search_query=param,
            skip=skip,
            limit=limit,
            current_user_id=current_user.id,
            bookshelf_id=bookshelf_id,
        )
        logger.info(
            "Searched for friends by param without bookshelf access",
            extra={
                "param": param,
                "user_id": current_user.id,
                "action": "search_for_param_friend",
            }
        )
    else:
        search_result = search_repo.get_friends_full_text_search(
            search_query=param, skip=skip, limit=limit, current_user_id=current_user.id
        )
        logger.info(
            "Searched for friends by param",
            extra={
                "param": param,
                "user_id": current_user.id,
                "action": "search_for_param_friend",
            }
        )

    return JSONResponse(content={"data": jsonable_encoder(search_result)})
