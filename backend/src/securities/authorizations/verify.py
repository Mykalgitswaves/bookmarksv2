from fastapi import HTTPException, status, Depends
from typing import Annotated
from jose import JWTError

from src.securities.authorizations.jwt import jwt_generator
from src.config.config import settings
from src.models.schemas.users import User
from src.database.graph.crud.users import UserCRUDRepositoryGraph
from src.api.utils.database import get_repository


async def get_current_user(token: Annotated[str, Depends(jwt_generator.oauth2_scheme)], 
                           user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        username = jwt_generator.retrieve_details_from_token(token, secret_key=settings.JWT_SECRET_KEY)
        if username is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    user = user_repo.get_user_by_username(username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user