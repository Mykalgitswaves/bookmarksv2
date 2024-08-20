import fastapi
from fastapi import HTTPException, Depends, BackgroundTasks, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated, Optional, List, Any

from src.api.utils.database import get_repository
from src.book_apis.google_books.search import google_books_search
from src.database.graph.crud.bookclubs import BookClubCRUDRepositoryGraph
from src.database.graph.crud.users import UserCRUDRepositoryGraph
from src.securities.authorizations.verify import get_current_active_user

router = fastapi.APIRouter(prefix="/bookclubs", tags=["bookclubs"])

### Create Book Club Form 1 ################################################################################################

router.post("/create",
            name="bookclub:create")
def create_bookclub(
        request: Request,
        bookclub_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> None:
    """
    Creates a bookclub for the current user. Bookclub is created upon
    selecting "Next"

    Args:
        request: The request object that contains the following attributes:
            user_id (str): User who submitted the request (validated with 
            current user)
            bookclub_name (str): Name of the bookclub
            bookclub_description (str): Description of the bookclub
            bookclub_pace (dict | None): OPTIONAL A dictionary that contains 
            the following attributes:
                        num_books (int): Number of books in interval (MAX 100)
                        num_time_period (int): Number of the respective time (MAX 100)
                        period
                        time_period (str): One of (days, weeks, months)
    Returns:
        200 success code

Raises:
        400 missing or invalid data fields
    """

### Invite Members Page ################################################################################################

router.get("/search/users/{param}",
            name="bookclub:search_users")
def search_users_not_in_club(
        param: str,
        user_repo: UserCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=UserCRUDRepositoryGraph))
) -> List[Any]:
    """
    Searches for existing users, excludes users already in the club

    Args:
        param (str): the search string

    Returns:
        users: an array of users that match the search string. User information
        contains:
            user_id(str): Id of the user
            user_username(str): username of the user
    """

router.put("/invite",
            name="bookclub:invite")
def invite_users_to_club(
        request: Request,
        bookclub_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> None:
    """
    Invites members to join the bookclub

    Args:
        request: The request object that contains the following atrtributes:
            user_ids Array[str]: An array of all the existing hardcover lit user ids to invite to the club
            emails Array[str]: An array of email addresses to send an invite to

    Returns:
        200 success code

    Raises:
        400 for invalid user_ids or invalid emails
    """

### Book Clubs Select Page ################################################################################################

router.get("/owned/{user_id}",
            name="bookclub:get_owned")
def get_owned_bookclubs(
        user_id: str,
        limit: Optional[int] = None,
        bookclub_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> List[Any]:
    """
    Gets all the clubs that the current user owns

    Args:
        user_id (str): The user id of the current user
        limit(int) OPTIONAL: If included, include only this many results (max)

    Returns:
        bookclubs (array): An array of bookclub object, each that contains:
            bookclub_name (str): Name of the bookclub
            pace (int | None): The number of chapeter ahead or behind of the club pace. None if no currently reading book
            currently_reading_book (Book| None): The book object for the current book which contains:
                book_title (str): The title of the current book
                book_img_url (str): The image for the current book
                book_id (str); The uuid for the current book
    """

router.get("/member/{user_id}",
            name="bookclub:get_member")
def get_member_bookclubs(
        user_id: str,
        limit: Optional[int] = None,
        bookclub_repo: BookClubCRUDRepositoryGraph = 
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
            pace (int | None): The number of chapeter ahead or behind of the club pace. None if no currently reading book
            currently_reading_book (Book| None): The book object for the current book which contains:
                book_title (str): The title of the current book
                book_img_url (str): The image for the current book
                book_id (str); The uuid for the current book
    """

### Book Club Invites Page ################################################################################################

router.get("/invites/{user_id}",
            name="bookclub:get_invites")
def get_bookclub_invites(
        user_id: str,
        limit: Optional[int] = None,
        bookclub_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> List[Any]:
    """
    Gets all the invites sent to the current user

    Args:
        user_id (str): The user id of the current user
        limit (int): Optional: the number of invites to include in the response (max)

    Returns:
        invites (array): an array of invites sent to the user, each invite includes:
            bookclub_id (str): The ID of the bookclub included in the invite
            bookclub_name (str): The name of the bookclub
            bookclub_owner_name (str): The user name of the bookclub owner
            num_mutual_friends (int): The number of mutual friends in the bookclub
    """

router.put("/invites/accept/{bookclub_id}",
            name="bookclub:accept_invite")
def accept_bookclub_invite(
        bookclub_id: str,
        bookclub_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> None:
    """
    Accepts an invite to join a bookclub

    Args:
        bookclub_id (str): The id of the bookclub to join

    Returns:
        200 success code

    Raises:
        404 if no invite exists
    """

router.put("/invites/decline/{bookclub_id}",
            name="bookclub:decline_invite")
def decline_bookclub_invite(
        bookclub_id: str,
        bookclub_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> None:
    """
    Declines an invite to join a bookclub

    Args:
        bookclub_id (str): The id of the bookclub to decline

    Returns:
        200 success code

    Raises:
        404 if no invite exists
    """