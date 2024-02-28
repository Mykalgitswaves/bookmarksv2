import fastapi
from fastapi import HTTPException, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated

from src.models.schemas.users import UserInResponse, User, UserUsername
from src.api.utils.database import get_repository
from src.database.graph.crud.users import UserCRUDRepositoryGraph
from src.securities.authorizations.verify import get_current_active_user

from src.securities.authorizations.jwt import jwt_generator
from src.models.schemas.token import Token

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

@router.get("/{user_id}/get_user",
            name="user:get_user")
async def get_complete_user(user_id: str, 
                            current_user: Annotated[User, Depends(get_current_active_user)],
                            user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):
    if not current_user:
        raise("400", "Unauthorized")
    if current_user and user_id:
        if current_user.id != user_id:
            relationship_to_current_user = 'anonymous'
        elif current_user.id == user_id:
            relationship_to_current_user = 'self'

        user = user_repo.get_user_for_settings(user_id=user_id, relationship_to_current_user=relationship_to_current_user)
        return JSONResponse(content={"data": jsonable_encoder(user)})
    
@router.put("/{user_id}/update_username",
            name="user:update_username")
async def update_username(request: Request, 
                          user_id: str, 
                          current_user: Annotated[User, Depends(get_current_active_user)],
                          user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):
    if not current_user:
        raise("400", "Unauthorized")
    if current_user.id == user_id:
        new_username = await request.json()
        
        try:
            new_username = UserUsername(username=new_username)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Check if the username is already taken
        username_taken = user_repo.is_username_taken(new_username.username)
        
        if username_taken:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Username is already taken")

        result = user_repo.update_username(new_username=new_username.username, user_id=user_id)
        if result.status_code == 200:
            access_token = jwt_generator.generate_access_token(username=new_username.username)

            return Token(
                access_token=access_token,
                token_type="bearer",
                user_id=user_id
            )
        else:
            return result
    else:
        raise HTTPException(400, detail="Unauthorized")
    
@router.put("/{user_id}/update_bio",
            name="user:update_bio")
async def update_bio(request: Request, 
                     user_id: str, 
                     current_user: Annotated[User, Depends(get_current_active_user)],
                     user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):
    if not current_user:
        raise("400", "Unauthorized")
    if current_user.id == user_id:
        new_bio = await request.json()
        response = user_repo.update_bio(user_id=user_id, new_bio=new_bio)
        if response:
            return HTTPException(200, detail="Success")
        else:
            raise HTTPException(401, detail="Unauthorized")
    else:
        raise HTTPException(400, detail="Unauthorized")