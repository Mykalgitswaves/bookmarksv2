import fastapi
from fastapi import HTTPException, Depends, Request, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated, Optional

from src.models.schemas.users import (
    UserInResponse,
    User,
    UserUsername,
    UserBio,
    UserEmail,
    UserProfileImg,
    UserPassword,
    UserId,
)
from src.models.schemas.social import (
    FriendRequestCreate,
    BlockUserCreate,
    FollowUserCreate,
    FriendDelete,
)
from src.api.utils.database import get_repository
from src.api.utils.helpers.login import is_strong_password
from src.database.graph.crud.users import UserCRUDRepositoryGraph
from src.securities.authorizations.verify import get_current_active_user

from src.securities.hashing.password import pwd_generator
from src.securities.authorizations.jwt import jwt_generator
from src.models.schemas.token import Token
from src.config.config import settings
from src.utils.logging.logger import logger

router = fastapi.APIRouter(prefix="/user", tags=["user"])


@router.get("/me", name="user:me", response_model=User)
def get_user_properties(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Get the properties of the current user.

    Parameters:
    - current_user: The current authenticated user.
    - user_repo: The repository for CRUD operations on user data.

    Returns:
    - The properties of the current user.
    """
    user = user_repo.get_user_properties(current_user.username)
    logger.info(
        "User properties retrieved",
        extra={
            "user_id": current_user.id,
            "action": "get_user_properties",
        },
    )
    return user


@router.get(
    "/me/liked_genres", name="user:me:liked_genres", response_model=dict[str, list[str]]
)
def get_user_liked_genres(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Get the genres liked by the current user.

    Parameters:
    - current_user: The current authenticated user.
    - user_repo: The repository for CRUD operations on user data.

    Returns:
    - A dictionary containing the liked genres of the current user.
    """
    genres = user_repo.get_user_liked_genres(current_user.username)
    logger.info(
        "User liked genres retrieved",
        extra={
            "user_id": current_user.id,
            "action": "get_user_liked_genres",
        },
    )
    return {"liked_genres": genres}


@router.get(
    "/me/liked_authors",
    name="user:me:liked_authors",
    response_model=dict[str, list[str]],
)
def get_user_liked_authors(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Get the authors liked by the current user.

    Parameters:
    - current_user: The current authenticated user.
    - user_repo: The repository for CRUD operations on user data.

    Returns:
    - A dictionary containing the liked authors of the current user.
    """
    authors = user_repo.get_user_liked_authors(current_user.username)
    logger.info(
        "User liked authors retrieved",
        extra={
            "user_id": current_user.id,
            "action": "get_user_liked_authors",
        },
    )
    return {"liked_authors": authors}


@router.get("/{user_id}/get_user", name="user:get_user")
async def get_complete_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    if current_user and user_id:
        if current_user.id != user_id:
            relationship_to_current_user = "anonymous"
        elif current_user.id == user_id:
            relationship_to_current_user = "self"

        user = user_repo.get_user_for_settings(
            user_id=user_id, relationship_to_current_user=relationship_to_current_user
        )
        logger.info(
            "User retrieved",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "get_complete_user",
            },
        )
        return JSONResponse(content={"data": jsonable_encoder(user)})


@router.put("/{user_id}/update_username", name="user:update_username")
async def update_username(
    request: Request,
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Updates a users email and refreshes the access token
    """

    if not current_user:
        raise HTTPException(400, "Unauthorized")
    if current_user.id == user_id:
        new_username = await request.json()

        try:
            new_username = UserUsername(username=new_username)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

        # Check if the username is already taken
        username_taken = user_repo.is_username_taken(new_username.username)

        if username_taken:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username is already taken"
            )

        result = user_repo.update_username(
            new_username=new_username.username, user_id=user_id
        )
        if result.status_code == 200:
            access_token = jwt_generator.generate_access_token(
                username=new_username.username
            )
            logger.info(
                "Username updated",
                extra={
                    "user_id": user_id,
                    "new_username": new_username.username,
                    "action": "update_username",
                },
            )
            return Token(
                access_token=access_token, token_type="bearer", user_id=user_id
            )
        else:
            logger.warning(
                "Error updating username",
                extra={
                    "user_id": user_id,
                    "new_username": new_username.username,
                    "action": "update_username",
                },
            )
            return result
    else:
        logger.warning(
            "Unauthorized user attempting to update username",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "update_username",
            },
        )
        raise HTTPException(400, detail="Unauthorized")


@router.put("/{user_id}/update_bio", name="user:update_bio")
async def update_bio(
    request: Request,
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Updates a users bio
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    if current_user.id == user_id:
        new_bio = await request.json()

        try:
            new_bio = UserBio(bio=new_bio)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

        response = user_repo.update_bio(user_id=user_id, new_bio=new_bio.bio)
        if response:
            logger.info(
                "User bio updated",
                extra={
                    "user_id": user_id,
                    "new_bio": new_bio.bio,
                    "action": "update_bio",
                },
            )
            return HTTPException(200, detail="Success")
        else:
            logger.warning(
                "Error updating user bio",
                extra={
                    "user_id": user_id,
                    "new_bio": new_bio.bio,
                    "action": "update_bio",
                },
            )
            raise HTTPException(401, detail="Unauthorized")
    else:
        logger.warning(
            "Unauthorized user attempting to update bio",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "update_bio",
            },
        )
        raise HTTPException(400, detail="Unauthorized")


@router.put("/{user_id}/update_email", name="user:update_email")
async def update_email(
    request: Request,
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Updates a user email. TODO: Send a confirmation email to the new email address.
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    if current_user.id == user_id:
        new_email = await request.json()
        try:
            new_email = UserEmail(email=new_email)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if len(new_email.email) > settings.SMALL_TEXT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=[{"msg": "Email is too long"}],
            )

        response = user_repo.update_email(user_id=user_id, new_email=new_email.email)
        if response:
            logger.info(
                "User email updated",
                extra={
                    "user_id": user_id,
                    "new_email": new_email.email,
                    "action": "update_email",
                },
            )
            return HTTPException(200, detail="Success")
        else:
            logger.warning(
                "Error updating user email",
                extra={
                    "user_id": user_id,
                    "new_email": new_email.email,
                    "action": "update_email",
                },
            )
            raise HTTPException(401, detail="Unauthorized")
    else:
        logger.warning(
            "Unauthorized user attempting to update email",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "update_email",
            },
        )
        raise HTTPException(400, detail="Unauthorized")


@router.put("/{user_id}/update_profile_img")
async def update_profile_img(
    request: Request,
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Updates a users profile image
    """
    profile_img_url = await request.json()
    if not profile_img_url:
        raise HTTPException(400, "Bad request brah, missing params")
    
    if current_user.id != user_id:
        logger.warning(
            "Unauthorized user attempting to update profile image",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "update_profile_img",
            },
        )
        raise HTTPException(400, "Unauthorized")
    
    try:
        profile_img_url = UserProfileImg(profile_img_url=profile_img_url["cdn_url"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = user_repo.update_user_profile_image(
        user_id=user_id, profile_img_url=profile_img_url.profile_img_url
    )
    if response:
        logger.info(
            "User profile image updated",
            extra={
                "user_id": user_id,
                "profile_img_url": profile_img_url.profile_img_url,
                "action": "update_profile_img",
            },
        )
        return JSONResponse(
            content={"data": jsonable_encoder(profile_img_url.profile_img_url)}
        )
    else:
        logger.warning(
            "Error updating user profile image",
            extra={
                "user_id": user_id,
                "profile_img_url": profile_img_url.profile_img_url,
                "action": "update_profile_img",
            },
        )
        raise HTTPException(401, detail="Unauthorized")


@router.put("/{user_id}/update_password", name="user:update_password")
async def update_password(
    request: Request,
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Changes the users password.
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    if current_user.id == user_id and request:
        new_password = await request.json()

        try:
            new_password = UserPassword(password=new_password)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=jsonable_encoder(e.json()))

        if not is_strong_password(new_password.password):
            logger.warning(
                "Password is not strong enough",
                extra={
                    "user_id": user_id,
                    "action": "update_password",
                },
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=[{"msg": "Password is not strong enough"}],
            )

        response = user_repo.update_password(
            new_password=pwd_generator.generate_hashed_password(new_password.password),
            user_id=user_id,
        )
        if response:
            logger.info(
                "User password updated",
                extra={
                    "user_id": user_id,
                    "action": "update_password",
                },
            )
            return HTTPException(200, detail="Success")
        else:
            logger.warning(
                "Error updating user password",
                extra={
                    "user_id": user_id,
                    "action": "update_password",
                },
            )
            raise HTTPException(401, detail="Unauthorized")

    else:
        logger.warning(
            "Unauthorized user attempting to update password",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "update_password",
            },
        )
        raise HTTPException(400, detail="Unauthorized")


@router.put("/{user_id}/send_friend_request/{friend_id}", name="user:send_friend_request")
async def send_friend_request(
    user_id: str,
    friend_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    This send a friend request from user_id -> friend_id
    """
    if current_user.id != user_id:
        raise HTTPException(400, "Unauthorized")

    try:
        friend_request = FriendRequestCreate(
            from_user_id=current_user.id, to_user_id=friend_id
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

    result = user_repo.create_friend_request(friend_request=friend_request)
    if result:
        logger.info(
            "Friend request sent",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": friend_id,
                "action": "send_friend_request",
            },
        )
        return HTTPException(200, detail="Success")
    else:
        logger.warning(
            "Error sending friend request",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": friend_id,
                "action": "send_friend_request",
            },
        )
        raise HTTPException(401, detail="Unauthorized")


@router.put("/{user_id}/unsend_friend_request/{friend_id}", name="user:unsend_friend_request")
async def unsend_friend_request(
    user_id: str,
    friend_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Unsends a friend request from user_id to friend_id
    """
    if current_user.id != user_id:
        raise HTTPException(400, "Unauthorized")
    try:
        friend_request = FriendRequestCreate(
            from_user_id=current_user.id, to_user_id=friend_id
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

    result = user_repo.delete_friend_request(friend_request=friend_request)
    if result:
        logger.info(
            "Friend request unsent",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": friend_id,
                "action": "unsend_friend_request",
            },
        )
        return HTTPException(200, detail="Success")
    else:
        logger.warning(
            "Error unsending friend request",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": friend_id,
                "action": "unsend_friend_request",
            },
        )
        raise HTTPException(401, detail="Unauthorized")


@router.put("/{friend_id}/accept_friend_request", name="user:accept_friend_request")
async def accept_friend_request(
    friend_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Accepts a friend request, checks that the request exists
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")

    try:
        friend_request = FriendRequestCreate(
            from_user_id=friend_id, to_user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

    result = user_repo.update_friend_request_to_accepted(friend_request)
    if result:
        logger.info(
            "Friend request accepted",
            extra={
                "from_user_id": friend_id,
                "to_user_id": current_user.id,
                "action": "accept_friend_request",
            },
        )
        return HTTPException(200, detail="Success")
    else:
        logger.warning(
            "Error accepting friend request",
            extra={
                "from_user_id": friend_id,
                "to_user_id": current_user.id,
                "action": "accept_friend_request",
            },
        )
        raise HTTPException(401, detail="Unauthorized")


@router.put("/{friend_id}/decline_friend_request", name="user:decline_friend_request")
async def decline_friend_request(
    friend_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Declines a friend request, checks that the request exists
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    try:
        friend_request = FriendRequestCreate(
            from_user_id=friend_id, to_user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

    result = user_repo.update_friend_request_to_declined(friend_request)
    if result:
        logger.info(
            "Friend request declined",
            extra={
                "from_user_id": friend_id,
                "to_user_id": current_user.id,
                "action": "decline_friend_request",
            },
        )
        return HTTPException(200, detail="Success")
    else:
        logger.warning(
            "Error declining friend request",
            extra={
                "from_user_id": friend_id,
                "to_user_id": current_user.id,
                "action": "decline_friend_request",
            },
        )
        raise HTTPException(401, detail="Unauthorized")


@router.put("/{friend_id}/remove_friend", name="user:remove_friend")
async def remove_friend(
    friend_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Removes a friend
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    try:
        friend_delete = FriendDelete(from_user_id=current_user.id, to_user_id=friend_id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

    result = user_repo.delete_friend_relationship(friend_delete)
    if result:
        logger.info(
            "Friend removed",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": friend_id,
                "action": "remove_friend",
            },
        )
        return HTTPException(200, detail="Success")
    else:
        logger.warning(
            "Error removing friend",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": friend_id,
                "action": "remove_friend",
            },
        )
        raise HTTPException(401, detail="Unauthorized")


@router.put("/{followed_user_id}/follow", name="user:follow_user")
async def follow_user(
    followed_user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Follows a user
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    try:
        follow_user = FollowUserCreate(
            from_user_id=current_user.id, to_user_id=followed_user_id
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    result = user_repo.create_follow_relationship(follow_user)
    if result:
        logger.info(
            "User followed",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": followed_user_id,
                "action": "follow_user",
            },
        )
        return HTTPException(200, detail="Success")
    else:
        logger.warning(
            "Error following user",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": followed_user_id,
                "action": "follow_user",
            },
        )
        raise HTTPException(401, detail="Unauthorized")


@router.put("/{unfollowed_user_id}/unfollow", name="user:unfollow_user")
async def unfollow_user(
    unfollowed_user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Unfollows a user
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    try:
        unfollow_user = FollowUserCreate(
            from_user_id=current_user.id, to_user_id=unfollowed_user_id
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    result = user_repo.delete_follow_relationship(unfollow_user)
    if result:
        logger.info(
            "User unfollowed",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": unfollowed_user_id,
                "action": "unfollow_user",
            },
        )
        return HTTPException(200, detail="Success")
    else:
        logger.warning(
            "Error unfollowing user",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": unfollowed_user_id,
                "action": "unfollow_user",
            },
        )
        raise HTTPException(401, detail="Unauthorized")


@router.put("/{blocked_user_id}/block", name="user:block_user")
async def block_user(
    blocked_user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Blocks a user
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    try:
        block_user = BlockUserCreate(
            from_user_id=current_user.id, to_user_id=blocked_user_id
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

    result = user_repo.create_blocked_relationship(block_user)
    if result:
        logger.info(
            "User blocked",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": blocked_user_id,
                "action": "block_user",
            },
        )
        return HTTPException(200, detail="Success")
    else:
        logger.warning(
            "Error blocking user",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": blocked_user_id,
                "action": "block_user",
            },
        )
        raise HTTPException(401, detail="Unauthorized")


@router.put("/{unblocked_user_id}/unblock", name="user:unblock_user")
async def unblock_user(
    unblocked_user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Unblocks a user
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    try:
        unblock_user = BlockUserCreate(
            from_user_id=current_user.id, to_user_id=unblocked_user_id
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    result = user_repo.delete_blocked_relationship(unblock_user)
    if result:
        logger.info(
            "User unblocked",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": unblocked_user_id,
                "action": "unblock_user",
            },
        )
        return HTTPException(200, detail="Success")
    else:
        logger.warning(
            "Error unblocking user",
            extra={
                "from_user_id": current_user.id,
                "to_user_id": unblocked_user_id,
                "action": "unblock_user",
            },
        )
        raise HTTPException(401, detail="Unauthorized")


@router.get("/{user_id}/user_about", name="user:user_about")
async def get_user_about(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Used for about me data called on user page.
    """
    try:
        user_id = UserId(id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not current_user:
        raise HTTPException(400, "Unauthorized")
    if current_user and user_id:
        user = user_repo.get_user_about_me(user_id=user_id.id)
        logger.info(
            "User about data retrieved",
            extra={
                "user_id": user_id.id,
                "current_user_id": current_user.id,
                "action": "get_user_about",
            },
        )
        return JSONResponse(content={"data": jsonable_encoder(user)})


@router.get("/{user_id}/friends", name="user:friends")
async def get_friend_list(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    includes_pending: Optional[str] = Query(
        None, description="Include a count of pending friend requests"
    ),
    bookshelf_id: Optional[str] = Query(
        None,
        description="Used to exclude existing contributors and members for a bookshelf suggested friends list.",
    ),
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Gets the friend list for the user as well as each friends relationship to the current user

    Args:
        includes_pending (Optional[str], optional): Include a count of pending friend requests, can only be requested by current user. Defaults to None.
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    if not user_id:
        raise HTTPException(400, "Bad request")

    if bookshelf_id:
        friend_list = user_repo.get_friend_list_no_bookshelf_access(
            user_id=user_id, current_user_id=current_user.id, bookshelf_id=bookshelf_id
        )
        if includes_pending:
            if current_user.id == user_id:
                pending_count = user_repo.get_pending_friend_count(user_id=user_id)
                logger.info(
                    "Friend list with pending count retrieved",
                    extra={
                        "user_id": user_id,
                        "current_user_id": current_user.id,
                        "bookshelf_id": bookshelf_id,
                        "num_friends": len(friend_list),
                        "action": "get_friend_list_no_bookshelf_access",
                    },
                )
                return JSONResponse(
                    content={
                        "friends": jsonable_encoder(friend_list),
                        "pending_count": jsonable_encoder(pending_count),
                    }
                )
        logger.info(
            "Friend list retrieved",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "bookshelf_id": bookshelf_id,
                "num_friends": len(friend_list),
                "action": "get_friend_list_no_bookshelf_access",
            },
        )
        return JSONResponse(content={"data": jsonable_encoder(friend_list)})
    else:
        friend_list = user_repo.get_friend_list(
            user_id=user_id, current_user_id=current_user.id
        )
        if includes_pending:
            if current_user.id == user_id:
                pending_count = user_repo.get_pending_friend_count(user_id=user_id)
                logger.info(
                    "Friend list with pending count retrieved",
                    extra={
                        "user_id": user_id,
                        "current_user_id": current_user.id,
                        "num_friends": len(friend_list),
                        "action": "get_friend_list",
                    },
                )
                return JSONResponse(
                    content={
                        "friends": jsonable_encoder(friend_list),
                        "pending_count": jsonable_encoder(pending_count),
                    }
                )
        logger.info(
            "Friend list retrieved",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "num_friends": len(friend_list),
                "action": "get_friend_list",
            },
        )
        return JSONResponse(content={"data": jsonable_encoder(friend_list)})


@router.get("/{user_id}/friend_requests", name="user:friend_requests")
async def get_friend_request_list(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Gets all the friend requests for the current user
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    if user_id == current_user.id:
        friend_request_list = user_repo.get_friend_request_list(user_id)
        logger.info(
            "Friend requests retrieved",
            extra={
                "user_id": user_id,
                "num_requests": len(friend_request_list),
                "action": "get_friend_requests",
            },
        )
        return JSONResponse(content={"data": jsonable_encoder(friend_request_list)})
    else:
        logger.warning(
            "Unauthorized user attempting to get friend requests",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "get_friend_requests",
            },
        )
        raise HTTPException(400, "Unauthorized")


@router.get("/{user_id}/blocked_users")
async def get_blocked_users_list(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Gets all the blocked users for the current user
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    if user_id == current_user.id:
        friend_request_list = user_repo.get_blocked_users_list(user_id)
        logger.info(
            "Blocked users retrieved",
            extra={
                "user_id": user_id,
                "num_blocked_users": len(friend_request_list),
                "action": "get_blocked_users",
            },
        )
        return JSONResponse(content={"data": jsonable_encoder(friend_request_list)})
    else:
        logger.warning(
            "Unauthorized user attempting to get blocked users",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "get_blocked_users",
            },
        )
        raise HTTPException(400, "Unauthorized")


@router.get("/{user_id}/activity")
async def get_activity_list(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
    skip: int | None = Query(default=0),
    limit: int | None = Query(default=10),
):
    """
    Gets all the recent activity for the user
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    if user_id == current_user.id:
        activity_list = user_repo.get_activity_list(
            current_user.username, user_id, skip, limit
        )
        logger.info(
            "Activity list retrieved",
            extra={
                "user_id": user_id,
                "num_activities": len(activity_list),
                "action": "get_activity_list",
            },
        )
        return JSONResponse(content={"data": jsonable_encoder(activity_list)})
    else:
        logger.warning(
            "Unauthorized user attempting to get activity list",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "get_activity_list",
            },
        )
        raise HTTPException(400, "Unauthorized")


@router.get("/{user_id}/suggested_friends", name="user:suggested_friends")
async def get_suggested_friends(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    n: int = 3,
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
):
    """
    Returns a list of n friends with the most mutual friends to the current user
    """
    if not current_user:
        raise HTTPException(400, "Unauthorized")
    if user_id == current_user.user_id:
        user_id = UserId(id=user_id)
        suggested_friends = user_repo.get_suggested_friends(user_id=user_id.id, n=n)
        logger.info(
            "Suggested friends retrieved",
            extra={
                "user_id": user_id.id,
                "num_suggested_friends": len(suggested_friends),
                "action": "get_suggested_friends",
            },
        )
        return JSONResponse(content={"data": jsonable_encoder(suggested_friends)})
    else:
        logger.warning(
            "Unauthorized user attempting to get suggested friends",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "get_suggested_friends",
            },
        )
        raise HTTPException(400, "Unauthorized")
