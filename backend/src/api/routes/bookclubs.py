import fastapi
from fastapi import HTTPException, Depends, BackgroundTasks, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated, Optional, List, Any, Mapping

from src.api.utils.database import get_repository
from src.book_apis.google_books.search import google_books_search
from src.database.graph.crud.bookclubs import BookClubCRUDRepositoryGraph
from src.database.graph.crud.users import UserCRUDRepositoryGraph
from src.models.schemas import bookclubs as BookClubSchemas
from src.models.schemas.users import User
from src.securities.authorizations.verify import get_current_active_user
from src.utils.helpers.email.email_client import email_client

router = fastapi.APIRouter(prefix="/bookclubs", tags=["bookclubs"])

### Create Book Club Form 1 ################################################################################################

@router.post("/create",
            name="bookclub:create")
async def create_bookclub(
        request: Request,
        current_user:  Annotated[User, Depends(get_current_active_user)],
        book_club_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> None:
    """
    Creates a bookclub for the current user. Bookclub is created upon
    selecting "Next"

    Args:
        request: The request object that contains the following attributes:
            user_id (str): User who submitted the request (validated with 
            current user)
            name (str): Name of the bookclub
            description (str): Description of the bookclub
            book_club_pace (dict | None): OPTIONAL A dictionary that contains 
            the following attributes:
                num_books (int): Number of books in interval (MAX 100)
                num_time_period (int): Number of the respective 
                time (MAX 100)
                period
                time_period (str): One of (days, weeks, months)
                name (str): Name of the pace
    Returns:
        book_club_id (str): The id of the bookclub created

    Raises:
        400 missing or invalid data fields
    """
    data = await request.json()

    if current_user.id != data.get("user_id"):
        raise HTTPException(status_code=400, detail="Invalid user_id")

    try:
        book_club = BookClubSchemas.BookClubCreate(**data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    response = book_club_repo.create_bookclub(book_club)

    if not response:
        raise HTTPException(
            status_code=400, 
            detail="Unable to create bookclub")
    else:
        return JSONResponse(
            status_code=200, 
            content={"book_club_id": response})

### Invite Members Page ################################################################################################

@router.get("/{book_club_id}/search/users/{param}",
            name="bookclub:search_users")
async def search_users_not_in_club(
        book_club_id: str,
        param: str,
        current_user:  Annotated[User, Depends(get_current_active_user)],
        limit: Optional[int] = 10,
        book_club_repo: BookClubCRUDRepositoryGraph =
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> List[Mapping[str, str]]:
    """
    Searches for existing users, excludes users already in the club

    Args:
        book_club_id (str): The id of the bookclub
        param (str): the search string

    Returns:
        users: an array of users that match the search string. User information
        contains:
            user_id(str): Id of the user
            user_username(str): username of the user
    """

    try:
        search_param = BookClubSchemas.BookClubInviteSearch(
            book_club_id=book_club_id,
            param=param,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    users = book_club_repo.search_users_not_in_club(search_param)

    return JSONResponse(content={"users":jsonable_encoder(users)})


@router.post("/invite",
            name="bookclub:invite")
async def invite_users_to_club(
        request: Request,
        current_user:  Annotated[User, Depends(get_current_active_user)],
        book_club_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> None:
    """
    Invites members to join the bookclub

    Args:
        request: The request object that contains the following atrtributes:
            user_ids Array[str]: An array of all the existing hardcover lit user 
            ids to invite to the club
            emails Array[str]: An array of email addresses to send an invite to
            book_club_id (str): The id of the bookclub to invite to

    Returns:
        200 success code

    Raises:
        400 for invalid user_ids or invalid emails
    """

    data = await request.json()

    try:
        invite = BookClubSchemas.BookClubInvite(
            book_club_id=data.get("book_club_id"),
            user_id=current_user.id,
            user_ids=data.get("user_ids"),
            emails=data.get("emails")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    response = book_club_repo.create_bookclub_invites(invite)
    
    for email in invite.emails:
        email_client.send_invite_email(
            email, 
            "Someone Invited You to Join a Book Club!")

    if not response:
        raise HTTPException(
            status_code=400, 
            detail="Unable to invite users to club")
    else:
        return JSONResponse(status_code=200, content={"message": "Invites sent"})

### Book Clubs Select Page ################################################################################################

@router.get("/owned/{user_id}",
            name="bookclub:get_owned")
async def get_owned_bookclubs(
        user_id: str,
        current_user:  Annotated[User, Depends(get_current_active_user)],
        limit: Optional[int] = None,
        book_club_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> List[Any]:
    """
    Gets all the clubs that the current user owns

    Args:
        user_id (str): The user id of the current user
        limit(int) OPTIONAL: If included, include only this many results (max)

    Returns:
        bookclubs (array): An array of bookclub object, each that contains:
            book_club_name (str): Name of the bookclub
            book_club_id(str): The uuid for the bookclub
            pace (int | None): The number of chapters ahead or behind of the 
            club pace. None if no currently reading book
            currently_reading_book (Book| None): The book object for the 
            current book which contains:
                book_title (str): The title of the current book
                book_img_url (str): The image for the current book
                book_id (str); The uuid for the current book
    """

    try:
        book_club_params = BookClubSchemas.BookClubList(
            user_id=user_id,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    book_clubs = book_club_repo.get_owned_book_clubs(book_club_params)

    return JSONResponse(content={"bookclubs":jsonable_encoder(book_clubs)})


@router.get("/member/{user_id}",
            name="bookclub:get_member")
async def get_member_bookclubs(
        user_id: str,
        current_user:  Annotated[User, Depends(get_current_active_user)],
        limit: Optional[int] = None,
        book_club_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> List[Any]:
    """
    Gets all the clubs that the current user is a member of

    Args:
        user_id (str): The user id of the current user
        limit(int) OPTIONAL: If included, include only this many results (max)

    Returns:
        bookclubs (array): An array of bookclub object, each that contains:
            bookclub_name (str): Name of the bookclub
            pace (int | None): The number of chapeter ahead or behind of the 
            club pace. None if no currently reading book
            currently_reading_book (Book| None): The book object for the 
            current book which contains:
                book_title (str): The title of the current book
                book_img_url (str): The image for the current book
                book_id (str); The uuid for the current book
    """

    try:
        book_club_params = BookClubSchemas.BookClubList(
            user_id=user_id,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    book_clubs = book_club_repo.get_member_book_clubs(book_club_params)

    return JSONResponse(content={"bookclubs":jsonable_encoder(book_clubs)})

### Book Club Invites Page ################################################################################################

@router.get("/invites/{user_id}",
            name="bookclub:get_invites")
def get_bookclub_invites(
        user_id: str,
        current_user:  Annotated[User, Depends(get_current_active_user)],
        limit: Optional[int] = None,
        book_club_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> List[Any]:
    """
    Gets all the invites sent to the current user

    Args:
        user_id (str): The user id of the current user
        limit (int): Optional: the number of invites to include in the 
        response (max)

    Returns:
        invites (array): an array of invites sent to the user, each invite 
        includes:
            invite_id (str): The id of the invite
            book_club_id (str): The ID of the bookclub included in the invite
            book_club_name (str): The name of the bookclub
            book_club_owner_name (str): The user name of the bookclub owner
            datetime_invited (datetime): The datetime the invite was sent
            num_mutual_friends (int): The number of mutual friends in the 
            bookclub
    """

    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail="Invalid user_id")
    
    try:
        invite_params = BookClubSchemas.BookClubList(
            user_id=user_id,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    invites = book_club_repo.get_book_club_invites(invite_params)

    return JSONResponse(content={"invites":jsonable_encoder(invites)})

@router.put("/invites/accept/{invite_id}",
            name="bookclub:accept_invite")
async def accept_bookclub_invite(
        invite_id: str,
        current_user:  Annotated[User, Depends(get_current_active_user)],
        book_club_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> None:
    """
    Accepts an invite to join a bookclub

    Args:
        invite_id (str): The id of the invite to accept

    Returns:
        200 success code

    Raises:
        404 if no invite exists
    """

    try:
        invite_params = BookClubSchemas.BookClubInviteResponse(
            invite_id=invite_id, 
            user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    response = book_club_repo.update_accept_book_club_invite(invite_params)

    if not response:
        raise HTTPException(
            status_code=404, 
            detail="Invite not found")
    else:
        return JSONResponse(status_code=200, content={"message": "Invite accepted"})

@router.put("/invites/decline/{invite_id}",
            name="bookclub:decline_invite")
async def decline_bookclub_invite(
        invite_id: str,
        current_user:  Annotated[User, Depends(get_current_active_user)],
        book_club_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> None:
    """
    Declines an invite to join a bookclub

    Args:
        invite_id (str): The id of the invite to decline

    Returns:
        200 success code

    Raises:
        404 if no invite exists
    """

    try:
        invite_params = BookClubSchemas.BookClubInviteResponse(
            invite_id=invite_id, 
            user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    response = book_club_repo.update_decline_book_club_invite(invite_params)

    if not response:
        raise HTTPException(
            status_code=404, 
            detail="Invite not found")
    else:
        return JSONResponse(status_code=200, content={"message": "Invite declined"})