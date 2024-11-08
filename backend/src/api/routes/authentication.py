import fastapi

from typing import Annotated
from fastapi import Depends, status, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.database.graph.crud.users import UserCRUDRepositoryGraph
from src.api.utils.database import get_repository
from src.api.utils.helpers.login import is_strong_password

from src.securities.authorizations.jwt import jwt_generator
from src.securities.hashing.password import pwd_generator

from src.models.schemas.users import (
    UserInResponse,
    UserCreate,
    UserLogin,
    User,
    UserToken,
)
from src.models.schemas.forms import SignUpForm, LoginForm
from src.models.schemas.token import Token
from src.securities.authorizations.verify import get_current_active_user
from src.config.config import settings
from src.utils.logging.logger import logger


router = fastapi.APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", name="auth:signup", response_model=Token)
async def signup(
    form_data: Annotated[SignUpForm, Depends()],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Create a new User

    Args:
        form_data (SignUpForm): The form data containing user details.
        user_repo (UserCRUDRepositoryGraph, optional): The user repository. Defaults to Depends(get_repository(repo_type=UserCRUDRepositoryGraph)).

    Raises:
        HTTPException: If the username or email is already taken.

    Returns:
        Token: The newly created user with access token.
    """
    try:
        user_create = UserCreate(
            username=form_data.username,
            email=form_data.email,
            password=form_data.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if len(user_create.email) > settings.SMALL_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is too long"
        )

    if not is_strong_password(user_create.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is not strong enough",
        )

    # Check if the username is already taken
    username_taken = user_repo.is_username_taken(user_create.username)
    # Check if the email is already taken
    email_taken = user_repo.is_email_taken(user_create.email)

    if username_taken:
        logger.debug("Username is already taken", extra={"username": user_create.username})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username is already taken"
        )
    elif email_taken:
        logger.debug("Email is already taken", extra={"email": user_create.email})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email is already taken"
        )

    # Generate a hashed password
    user_create.password = pwd_generator.generate_hashed_password(user_create.password)
    # Create a new user
    new_user = user_repo.create_user(user_create=user_create)
    # Generate an access token
    access_token = jwt_generator.generate_access_token(username=new_user.username)

    logger.info("User created", extra={"username": new_user.username, "email": new_user.email, "action": "signup"})

    return Token(access_token=access_token, token_type="bearer", user_id=new_user.id)


@router.post("/login", name="auth:login", response_model=Token)
async def login(
    form_data: Annotated[LoginForm, Depends()],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Authenticate User

    Args:
        form_data (LoginForm): The form data containing user login details.
        user_repo (UserCRUDRepositoryGraph, optional): The user repository.
            Defaults to Depends(get_repository(repo_type=UserCRUDRepositoryGraph)).

    Raises:
        HTTPException: If the user is not found or the password is invalid.

    Returns:
        Token: The authenticated user with access token.
    """
    if form_data.email:
        try:
            user = UserLogin(email=form_data.email, password=form_data.password)
            user.email = user.email.lower()
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        # Check if the user exists in the database
        user_in_db = user_repo.get_user_by_email(email=user.email)
    elif form_data.username:
        try:
            user = UserToken(username=form_data.username, password=form_data.password)
            user.username = user.username.lower()
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        user_in_db = user_repo.get_user_by_username(username=user.username)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid form data"
        )

    # Check if the user exists in the database
    if not user_in_db:
        logger.warning("User not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username or password incorrect",
        )

    # Check if the password is valid
    if not pwd_generator.is_password_authenticated(user.password, user_in_db.password):
        logger.warning(f"Password incorrect for user: {user_in_db.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password incorrect",
        )

    # Generate access token
    access_token = jwt_generator.generate_access_token(username=user_in_db.username)

    # Return the authenticated user with access token
    logger.info("User logged in", extra={"username": user_in_db.username, "email": user_in_db.email, "action": "login"})
    return Token(access_token=access_token, token_type="bearer", user_id=user_in_db.id)


@router.get("/verify", name="auth:verify")
async def verify(
    request: Request, current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Verify User

    Args:
        request (Request): The HTTP request object.
        current_user (User): The current authenticated user.

    Returns:
        HTTPException: If the UUID and access token don't match or if the UUID or access token is missing.
    """
    # Get the UUID from the query parameters
    uuid = request.query_params["uuid"]

    # Check if both UUID and current_user are present
    if uuid and current_user:
        # Check if the UUID matches the current user's ID
        if uuid == current_user.id:
            # Return HTTPException with status code 200 and detail message
            return HTTPException(
                status_code=200, detail="User is validated"
            )  # User is validated
        else:
            # Return HTTPException with status code 401, detail message, and WWW-Authenticate header
            validation_error = HTTPException(
                status_code=401,
                detail="uuid and access token dont match",
                headers={"WWW-Authenticate": "Bearer"},
            )
            return validation_error
    else:
        # Return HTTPException with status code 401, detail message, and WWW-Authenticate header
        validation_error = HTTPException(
            status_code=401,
            detail="Missing uuid or access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        return validation_error
