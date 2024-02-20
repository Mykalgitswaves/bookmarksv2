import fastapi
from fastapi import HTTPException, Depends
from typing import Annotated

from src.models.schemas.users import UserInResponse, User
from src.api.utils.database import get_repository
from src.database.graph.crud.users import UserCRUDRepositoryGraph
from src.securities.authorizations.verify import get_current_active_user

router = fastapi.APIRouter(prefix="/user", tags=["user"])

@router.get("/me",
            name="user:me",
            response_model=User)
def get_user_properties(current_user:  Annotated[User, Depends(get_current_active_user)],
             user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):          
    """
    Get the properties of the current user.

    Parameters:
    - current_user: The current authenticated user.
    - user_repo: The repository for CRUD operations on user data.

    Returns:
    - The properties of the current user.
    """
    user = user_repo.get_user_properties(current_user.username)
    return user

@router.get("/me/liked_genres",
            name="user:me:liked_genres",
            response_model=dict[str, list[str]])
def get_user_liked_genres(current_user:  Annotated[User, Depends(get_current_active_user)],
             user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):          
    """
    Get the genres liked by the current user.

    Parameters:
    - current_user: The current authenticated user.
    - user_repo: The repository for CRUD operations on user data.

    Returns:
    - A dictionary containing the liked genres of the current user.
    """
    genres = user_repo.get_user_liked_genres(current_user.username)
    return {"liked_genres": genres}

@router.get("/me/liked_authors",
            name="user:me:liked_authors",
            response_model=dict[str, list[str]])
def get_user_liked_genres(current_user:  Annotated[User, Depends(get_current_active_user)],
             user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):          
    """
    Get the authors liked by the current user.

    Parameters:
    - current_user: The current authenticated user.
    - user_repo: The repository for CRUD operations on user data.

    Returns:
    - A dictionary containing the liked authors of the current user.
    """
    authors = user_repo.get_user_liked_authors(current_user.username)
    return {"liked_authors": authors}
