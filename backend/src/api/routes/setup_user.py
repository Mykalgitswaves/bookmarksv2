import fastapi
from fastapi import HTTPException, Depends, Request

from typing import Annotated

from src.securities.authorizations.verify import get_current_active_user
from src.models.schemas.users import UserInResponse, User
from src.models.schemas.setup_user import SetupUserFullName, SetupUserGenres, SetupUserAuthors
from src.api.utils.database import get_repository
from src.database.graph.crud.users import UserCRUDRepositoryGraph

router = fastapi.APIRouter(prefix="/setup-user", tags=["setup-user"])

@router.put("/full_name",
            name="setup-user:full_name")
async def setup_user_full_name(request:Request, 
                          current_user:  Annotated[User, Depends(get_current_active_user)],
                          user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):
    """
    Update the full name of the current user.

    Args:
        request (Request): The incoming request.
        current_user (User): The current authenticated user.
        user_repo (UserCRUDRepositoryGraph): The repository for user CRUD operations.

    Returns:
        HTTPException: Returns HTTPException with status code 200 if the update is successful.
                       Returns HTTPException with status code 404 if the user is not found.
                       Returns HTTPException with status code 500 if there is an internal error.
    """
    # Parse the request body to get the setup_user_obj
    setup_user_obj = SetupUserFullName(**(await request.json()))

    # Check if the current user is authenticated
    if current_user:
        try:
            # Update the full name of the current user in the user repository
            user = user_repo.update_user_full_name(username=current_user.username, full_name=setup_user_obj.full_name)
            
            # Check if the user is found and the update is successful
            if user is not None:
                return HTTPException(
                    status_code=200,
                    detail="SUCCESS DUDE"
                )
            else:
                # Return HTTPException with status code 404 if the user is not found
                return HTTPException(
                    status_code=404,
                    detail="User not found"
                )

        except:
            # Return HTTPException with status code 500 if there is an internal error
            return HTTPException(
                status_code=500,
                detail="Internal error, try again later"
            )
        
@router.put("/genres",
            name="setup-user:genres")
async def setup_user_genres(request:Request, 
                          current_user:  Annotated[User, Depends(get_current_active_user)],
                          user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):
    """
    Update the liked genres of the current user.

    Args:
        request (Request): The incoming request.
        current_user (User): The current authenticated user.
        user_repo (UserCRUDRepositoryGraph): The repository for user CRUD operations.

    Returns:
        HTTPException: Returns HTTPException with status code 200 if the update is successful.
                       Returns HTTPException with status code 404 if the genre or user is not found.
    """
    # Parse the request body into a SetupUserGenres object
    setup_user_genres = SetupUserGenres(**(await request.json()))

    try:
        # Iterate through the genres in the request
        for genre in setup_user_genres.genres:
            # Update the user's liked genre in the repository
            response = user_repo.update_user_liked_genre(genre_id=genre, username=current_user.username)
            if not response:
                # Return HTTPException with status code 404 if the genre or user is not found
                return HTTPException(
                    status_code=404,
                    detail="Genre or User not found"
                )
    except:
        # Return a network error HTTPException if an exception occurs during setup
        network_error = HTTPException(
                status_code=404,
                detail="Network error occurred during setup, please try again later",
                headers={"WWW-Authenticate": "Bearer"},
                )
        return network_error
    
    # Return HTTPException with status code 200 if the update is successful
    return HTTPException(
        status_code=200,
        detail="success"
    )

@router.put("/authors",
            name="setup-user:authors")
async def setup_user_authors(request:Request,
                            current_user:  Annotated[User, Depends(get_current_active_user)],
                            user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):
    """
    Update the liked authors of the current user.

    Args:
        request (Request): The incoming request.
        current_user (User): The current authenticated user.
        user_repo (UserCRUDRepositoryGraph): The repository for user CRUD operations.

    Returns:
        HTTPException: Returns HTTPException with status code 200 if the update is successful.
                       Returns HTTPException with status code 404 if the author or user is not found.
    """
    # Create an instance of SetupUserAuthors from the request JSON data
    try:
        setup_user_authors = SetupUserAuthors(**(await request.json()))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # Iterate through the authors in the setup_user_authors object
        for author in setup_user_authors.authors:
            # Update the liked author for the current user in the user repository
            response = user_repo.update_user_liked_author(author_id=author, username=current_user.username)
            
            # If the response is False, return HTTPException with status code 404
            if not response:
                return HTTPException(
                    status_code=404,
                    detail="Author or User not found"
                )
    except:
        # If an exception occurs, return a network error HTTPException with status code 404
        network_error = HTTPException(
                status_code=404,
                detail="Network error occurred during setup, please try again later",
                headers={"WWW-Authenticate": "Bearer"},
                )
        return network_error
    
    # Return a success HTTPException with status code 200
    return HTTPException(
        status_code=200,
        detail="success"
    )