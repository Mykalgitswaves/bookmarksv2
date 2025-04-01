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
from src.book_apis.open_library.search import open_library_search
from src.utils.logging.logger import logger

router = fastapi.APIRouter(prefix="/search", tags=["search"])


@router.get("/{param}", name="search:full")
async def search_for_param(
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

    # books_result = google_books_search.search(param, skip, limit)
    books_result = open_library_search.search(param, skip, limit)
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
async def search_for_param_book(param: str, skip: int = 0, limit: int = 5):
    """
    Endpoint used for searching for users, todo add in credentials for searching
    """

    # books_result = google_books_search.search(param, skip, limit)
    books_result = open_library_search.search(param, skip, limit)
    logger.info(
        "Search for param in google books",
        extra={
            "param": param,
            "action": "search_for_param_book",
        }
    )

    return JSONResponse(content={"data": jsonable_encoder(books_result)})


@router.get("/users/{param}", name="search:users")
async def search_for_param_user(
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
async def search_for_param_friend(
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

@router.get("/bookclubs/{param}", name="search:bookclubs")
async def search_for_param_bookclub(
    param: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 5,
    search_repo: SearchCRUDRepositoryGraph = Depends(
        get_repository(repo_type=SearchCRUDRepositoryGraph)
    ),
):
    """
    Searches book clubs by name and description.

    Args:
        param (str): The search query.
        current_user (User): The current user.
        skip (int): The number of records to skip.
        limit (int): The number of records to return.
        search_repo (SearchCRUDRepositoryGraph): The search repository.
    
    Returns:
        JSONResponse: The search results.
    """

    search_result = search_repo.get_bookclubs_full_text_search(
        search_query=param, skip=skip, limit=limit
    )

    logger.info(
        "Searched for bookclubs by param",
        extra={
            "param": param,
            "user_id": current_user.id,
            "action": "search_for_param_bookclub",
        }
    )

    return JSONResponse(content={"data": jsonable_encoder(search_result)})

@router.get("/bookshelves/{param}", name="search:bookshelves")
async def search_for_param_bookshelf(
    param: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 5,
    search_repo: SearchCRUDRepositoryGraph = Depends(
        get_repository(repo_type=SearchCRUDRepositoryGraph)
    ),
):
    """
    Searches book shelves by name and description.

    Args:
        param (str): The search query.
        current_user (User): The current user.
        skip (int): The number of records to skip.
        limit (int): The number of records to return.
        search_repo (SearchCRUDRepositoryGraph): The search repository.
    
    Returns:
        id (str): The ID of the bookshelf.
        name (str): The name of the bookshelf.
        description (str): The description of the bookshelf.
        number_of_books (int): The number of books in the bookshelf.
        owner_username (str): The username of the owner of the bookshelf.
        first_book (dict): The first book in the bookshelf. This contains:
            id (str): The ID of the book.
            title (str): The title of the book.
            small_img_url (str): The small image URL of the book.
    """

    search_result = search_repo.get_bookshelves_full_text_search(
        search_query=param, skip=skip, limit=limit
    )

    logger.info(
        "Searched for bookshelfs by param",
        extra={
            "param": param,
            "user_id": current_user.id,
            "action": "search_for_param_bookshelf",
        }
    )

    return JSONResponse(content={"data": jsonable_encoder(search_result)})