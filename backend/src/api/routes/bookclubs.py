from datetime import datetime, timezone
import fastapi
from fastapi import HTTPException, Depends, BackgroundTasks, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated, Optional, List, Any, Mapping
from neo4j.time import DateTime

from src.api.background_tasks.google_books import google_books_background_tasks
from src.api.utils.database import get_repository
from src.book_apis.google_books.search import google_books_search
from src.book_apis.google_books.pull_books import google_books_pull
from src.database.graph.crud.books import BookCRUDRepositoryGraph
from src.database.graph.crud.bookclubs import BookClubCRUDRepositoryGraph
from src.database.graph.crud.users import UserCRUDRepositoryGraph
from src.models.schemas import bookclubs as BookClubSchemas
from src.models.schemas import posts as PostSchemas
from src.models.schemas.users import User, UserId
from src.securities.authorizations.verify import get_current_active_user
from src.utils.helpers.email.email_client import email_client
from src.utils.logging.logger import logger

router = fastapi.APIRouter(prefix="/bookclubs", tags=["bookclubs"])

### Create Book Club Form 1 ################################################################################################


@router.post("/create", name="bookclub:create")
async def create_bookclub(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
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
        logger.warning(
            "User id does not match current user id",
            extra={
                "user_id": data.get("user_id"),
                "current_user_id": current_user.id,
                "action": "create_bookclub",
            }
        )
        raise HTTPException(status_code=400, detail="Invalid user_id")

    try:
        book_club = BookClubSchemas.BookClubCreate(**data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = book_club_repo.create_bookclub(book_club)

    if not response:
        logger.warning(
            "Unable to create bookclub",
            extra={
                "user_id": current_user.id,
                "book_club_name": book_club.name,
                "action": "create_bookclub",
            }
        )
        raise HTTPException(status_code=400, detail="Unable to create bookclub")
    else:
        logger.info(
            "Bookclub created",
            extra={
                "user_id": current_user.id,
                "book_club_id": response,
                "book_club_name": book_club.name,
                "action": "create_bookclub",
            }
        )
        return JSONResponse(status_code=200, content={"book_club_id": response})


@router.put("/{book_club_id}/update_metadata", name="bookclub:update_metadata")
async def update_club_metadata(
    request: Request,
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> None:
    """
    Update the description of a book club that you own.

    Args: book_club_id (str): The id of the bookclub

    Returns:
        None
    """

    try:
        data = await request.json()
        
        # Validate required fields
        if "title" not in data or "description" not in data:
            raise ValueError("Missing required fields: title and description")
            
        # Create a clean data dictionary with only the fields we need
        clean_data = {
            "title": data.get("title"),
            "description": data.get("description")
        }

        updated_club_metadata = book_club_repo.update_club_metadata(
            book_club_id=book_club_id, 
            user_id=current_user.id,
            updated_data=clean_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"club": updated_club_metadata})


### Invite Members Page ################################################################################################


@router.get("/{book_club_id}/search/users/{param}", name="bookclub:search_users")
async def search_users_not_in_club(
    book_club_id: str,
    param: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: Optional[int] = 10,
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
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
            book_club_id=book_club_id, param=param, limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    users = book_club_repo.search_users_not_in_club(search_param)

    logger.info(
        "Searched for users not in club",
        extra={
            "user_id": current_user.id,
            "book_club_id": book_club_id,
            "action": "search_users_not_in_club",
        }
    )
    return JSONResponse(content={"users": jsonable_encoder(users)})

# TODO: delete this shit
@router.post("/invite_legacy",
            name="bookclub:invite")
async def invite_users_to_club(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
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
            emails=data.get("emails"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = book_club_repo.create_bookclub_invites_dep(invite)

    for email in invite.emails:
        # email_client.send_invite_email(
        #     email, "Someone Invited You to Join a Book Club!"
        # )
        pass

    if not response:
        raise HTTPException(status_code=400, detail="Unable to invite users to club")
    else:
        return JSONResponse(status_code=200, content={"message": "Invites sent"})
    
@router.post("/invite",
            name="bookclub:invite_new")
async def invite_users_to_club_new(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    background_tasks: BackgroundTasks,
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> None:
    """
    Invites members to join the bookclub. One of user_id or email must be
    present

    Args:
        request: The request object that contains the following attributes:
            invites: a dictionary that contains the following key:
                (key) temp_id: The temporary id for the invite:
                (value) a dictionary that contains the following fields:
                    user_id: OPTIONAL the user_id to invite to the club
                    email: OPTIONAL the email to invite to the club
            book_club_id: the id of the bookclub


        example:
            {
                0: {
                    "user_id": "bigpapi420"
                },
                1: {
                    "user_id": "smallpapi419"
                },
                2: {
                    "email": "email@email.com"
                }
            }

    Returns:
        a dictionary of the temp ids, permanent ids, and status

        example:
            {
                0: {
                    "id": "club_invite_uuid_1",
                    "status": "invite_sent"
                },
                1: {
                    "id": "club_invite_uuid_2",
                    "status": "error"
                },
                2: {
                    "id": "club_invite_uuid_3",
                    "status": "already_member"
                }
            }

    Raises:
        400 for invalid user_ids or invalid emails
    """

    data = await request.json()

    invites = data.get("invites")
    user_ids = [
        invites[item].get("user_id")
        for item in invites
        if (
            invites[item].get("user_id")
            and invites[item].get("user_id") != current_user.id
        )
    ]

    emails = [
        invites[item].get("email")
        for item in invites
        if invites[item].get("email") and not invites[item].get("user_ids")
    ]

    if not user_ids and not emails:
        logger.warning(
            "No data sent",
            extra={
                "user_id": current_user.id, 
                "action": "invite_users_to_club"
            },
        )
        raise HTTPException(status_code=400, detail="No data sent")

    try:
        invite_obj = BookClubSchemas.BookClubInvite(
            book_club_id=data.get("book_club_id"),
            user_id=current_user.id,
            user_ids=user_ids,
            emails=emails,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = book_club_repo.create_bookclub_invites(invite_obj)

    if invite_obj.emails:
        for email in invite_obj.emails:
            if email in response:
                if response[email]['status'] != "already_member":
                    # print(response[email])
                    background_tasks.add_task(
                        email_client.send_invite_email,
                        email,
                        response[email]['id'],
                        invite_obj.book_club_id,
                        current_user.username,
                        "Someone Invited You to Join a Book Club!",
                        book_club_repo
                    )

    for item in invites:
        invite = invites[item]
        if invite.get("user_id"):
            if not response.get(invite.get("user_id")):
                invite.update({"status": "error"})
            else:
                invite.update({"status": response[invite.get("user_id")].get("status")})
                if response.get(invite.get("user_id")).get("id"):
                    invite.update({"id": response[invite.get("user_id")].get("id")})

        elif invite.get("email"):
            if not response.get(invite.get("email")):
                invite.update({"status": "error"})
            else:
                invite.update({"status": response[invite.get("email")].get("status")})
                if response.get(invite.get("email")).get("id"):
                    invite.update({"id": response[invite.get("email")].get("id")})

    logger.info(
        "Invited users to club",
        extra={
            "user_id": current_user.id,
            "book_club_id": invite_obj.book_club_id,
            "num_invites": len(invites),
            "action": "invite_users_to_club",
        },
    )
    return invites


### Book Clubs Select Page ################################################################################################


@router.get("/owned/{user_id}", name="bookclub:get_owned")
async def get_owned_bookclubs(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: Optional[int] = None,
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
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
        book_club_params = BookClubSchemas.BookClubList(user_id=user_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    book_clubs = book_club_repo.get_owned_book_clubs(book_club_params)
    
    logger.info(
        "Fetched owned book clubs",
        extra={
            "user_id": current_user.id,
            "num_book_clubs": len(book_clubs),
            "action": "get_owned_bookclubs",
        },
    )

    return JSONResponse(content={"bookclubs": jsonable_encoder(book_clubs)})


@router.get("/member/{user_id}", name="bookclub:get_member")
async def get_member_bookclubs(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: Optional[int] = None,
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
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
        book_club_params = BookClubSchemas.BookClubList(user_id=user_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    book_clubs = book_club_repo.get_member_book_clubs(book_club_params)
    
    logger.info(
        "Fetched member book clubs",
        extra={
            "user_id": current_user.id,
            "num_book_clubs": len(book_clubs),
            "action": "get_member_bookclubs",
        },
    )

    return JSONResponse(content={"bookclubs": jsonable_encoder(book_clubs)})


### Book Club Invites Page ################################################################################################


@router.get("/invites/{user_id}", name="bookclub:get_invites")
def get_bookclub_invites(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: Optional[int] = None,
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
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
        logger.warning(
            "User id does not match current user id",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "get_bookclub_invites",
            },
        )
        raise HTTPException(status_code=400, detail="Invalid user_id")

    try:
        invite_params = BookClubSchemas.BookClubList(user_id=user_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    invites = book_club_repo.get_book_club_invites(invite_params)
    logger.info(
        "Fetched book club invites",
        extra={
            "user_id": current_user.id,
            "num_invites": len(invites),
            "action": "get_bookclub_invites",
        },
    )
    return JSONResponse(content={"invites": jsonable_encoder(invites)})


@router.put("/invites/accept/{invite_id}", name="bookclub:accept_invite")
async def accept_bookclub_invite(
    invite_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
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
            invite_id=invite_id, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = book_club_repo.update_accept_book_club_invite(invite_params)

    if not response:
        logger.warning(
            "Unable to accept bookclub invite",
            extra={
                "user_id": current_user.id,
                "invite_id": invite_id,
                "action": "accept_bookclub_invite",
            },
        )
        raise HTTPException(status_code=404, detail="Invite not found")
    else:
        logger.info(
            "Accepted book club invite",
            extra={
                "user_id": current_user.id,
                "invite_id": invite_id,
                "action": "accept_bookclub_invite",
            },
        )
        return JSONResponse(status_code=200, content={"message": "Invite accepted"})


@router.put("/invites/decline/{invite_id}", name="bookclub:decline_invite")
async def decline_bookclub_invite(
    invite_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
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
            invite_id=invite_id, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = book_club_repo.update_decline_book_club_invite(invite_params)

    if not response:
        logger.warning(
            "Unable to decline bookclub invite",
            extra={
                "user_id": current_user.id,
                "invite_id": invite_id,
                "action": "decline_bookclub_invite",
            },
        )
        raise HTTPException(status_code=404, detail="Invite not found")
    else:
        logger.info(
            "Declined book club invite",
            extra={
                "user_id": current_user.id,
                "invite_id": invite_id,
                "action": "decline_bookclub_invite",
            },
        )
        return JSONResponse(status_code=200, content={"message": "Invite declined"})


@router.get(
    "/{book_club_id}/members/{user_id}", name="bookclub:get_members_for_book_club"
)
async def get_members_for_book_club(
    book_club_id: str,
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> list:
    """
    Returns a list of members for a book_club
    """
    # We should maybe think about doing this implicitly with some decorator, since we repeat it so many places.
    if current_user.id != user_id:
        logger.warning(
            "User id does not match current user id",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "get_members_for_book_club",
            },
        )
        raise HTTPException(status_code=400, detail="Unauthorized")
    
    book_club_members = book_club_repo.get_members_for_book_club(
        book_club_id=book_club_id, user_id=user_id
    )

    logger.info(
        "Fetched members for book club",
        extra={
            "user_id": current_user.id,
            "book_club_id": book_club_id,
            "num_members": len(book_club_members),
            "action": "get_members_for_book_club",
        },
    )
    return JSONResponse(content={"members": jsonable_encoder(book_club_members)})

@router.get(
    "/{book_club_id}/minimal_preview/{user_id}/user", name="bookclub:minimal_preview"
)
async def get_book_club_minimal_preview(
    book_club_id: str,
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
):
    """Initial get request for grabbing the book club data.
    
    Args:
        book_club_id: The id of the book club
        user_id: The current users id
        
    Returns:
        book_club: An object containing the following:
            book_club_id (str): The id of the book club
            book_club_name (str): The name of the book club
            book_club_description (str): The description of the book club
            currently_reading (dict | None): An object describing the book the club
                is currently reading. If present, this contains:
                    book_id (str): The id of the book
                    title (str): The title of the book
                    small_img_url (str): The img url for the book
                    is_user_finished_currently_reading: (bool) has a user finished reading the current_reading_book
            pace (int | None): The pace offset between the expected chapter of the reader 
                based on the clubs expected finish date. If negative, the reader is n chapters
                behind the clubs expected pace. If positive, the reader is n chapters ahead
                of the clubs expected pace.
    """
    if current_user.id != user_id:
        logger.warning(
            "User id does not match current user id",
            extra={
                "user_id": user_id,
                "current_user_id": current_user.id,
                "action": "get_book_club_minimal_preview",
            },
        )
        raise HTTPException(status_code=400, detail="Unauthorized")

    try:
        book_club = book_club_repo.get_minimal_book_club(
            book_club_id=book_club_id, user_id=user_id
        )
    except:
        raise HTTPException(status_code=404, detail="Bookclub not found")

    logger.info(
        "Fetched minimal preview for book club",
        extra={
            "user_id": current_user.id,
            "book_club_id": book_club_id,
            "action": "get_book_club_minimal_preview",
        },
    )
    return JSONResponse(content={"book_club": jsonable_encoder(book_club)})


### Club feed page ################################################################################################

@router.get("/{book_club_id}/user_pace", name="bookclub:user_pace")
async def get_user_pace(
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> Any:
    """
    Gets the users pace, the expected pace of the club, and the average pace of
    the club

    Args:
        book_club_id: The id of the bookclub to get

    Returns:
        paces: a dictionary object that contains the following values:
        expected_pace (int): The expected chapter based on the estimated finish
            date of the club, rounded to the closest int
        user_pace (int): The current chapter of the user
        club_pace (int): The average chapter of the club members, rounded to
            the closest int
        total_chapters (int): The total number of chapters, inputted by the
            club admin
    """

    paces = book_club_repo.get_user_pace(book_club_id, current_user.id)

    if paces:
        logger.info(
            "Fetched user pace",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "action": "get_user_pace",
            },
        )
        return JSONResponse(status_code=200, content={"paces": jsonable_encoder(paces)})
    else:
        logger.warning(
            "Unable to fetch user pace",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "action": "get_user_pace",
            },
        )
        raise HTTPException(status_code=404, detail="Invite not found")


@router.get("/{book_club_id}/club_members_pace", name="bookclub:club_members_pace")
async def get_club_members_pace(
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> Any:
    """
    Gets the current chapter of each member in the club

    Args:
        book_club_id: The id of the book club to get

    Returns:
        member_paces (array): an array, where each object is a dictionary which
        contains the following values. The array is sorted by member_pace
        descending:
            id (str): the uuid of the member
            username (str): the username of the member
            pace (int):  the current chapter of the member
            is_current_user (bool): Flag for if this member is the current user
    """

    member_paces = book_club_repo.get_member_paces(book_club_id, current_user.id)

    if member_paces is not None:
        logger.info(
            "Fetched club member paces",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "num_paces": len(member_paces),
                "action": "get_club_members_pace",
            },
        )
        return JSONResponse(
            status_code=200, content={"member_paces": jsonable_encoder(member_paces)}
        )
    else:
        logger.warning(
            "Unable to fetch club member paces",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "action": "get_club_members_pace",
            },
        )
        raise HTTPException(status_code=404, detail="Invite not found")


@router.post("/{book_club_id}/update/create", name="bookclub:update_create")
async def create_update_post_club(
    request: Request,
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> None:
    """
    Creates an update post for the book club

    Args:
        request: A request object that contains the following fields:
            user (dict): A user object containing the following fields:
                id (str): The id of the user
            chapter (int): The chapter that the update is posted for
            response (str | None): The response that was created with the update
            headline (str): The headline for the post
            quote (str): The quote to include with the post

    Returns:
        200 response for a successful post
    """
    data = await request.json()

    if not data.get("user"):
        logger.warning(
            "User is a required field",
            extra={
                "user_id": current_user.id,
                "action": "create_update_post_club",
            },
        )
        raise HTTPException(status_code=400, detail="User is a required field")

    if data.get("user").get("id") != current_user.id:
        logger.warning(
            "User id does not match current user id",
            extra={
                "user_id": data.get("user").get("id"),
                "current_user_id": current_user.id,
                "action": "create_update_post_club",
            },
        )
        raise HTTPException(status_code=400, detail="Unauthorized")

    try:
        update_data = BookClubSchemas.CreateUpdatePost(
            user=data.get("user"),
            chapter=data.get("chapter"),
            response=data.get("response"),
            headline=data.get("headline"),
            id=book_club_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if update_data.response:
        response = book_club_repo.create_update_post(update_data)
    else:
        response = book_club_repo.create_update_post_no_text(update_data)

    if response:
        logger.info(
            "Created update post for club",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "chapter": update_data.chapter,
                "action": "create_update_post_club",
            },
        )
        return JSONResponse(status_code=200, content={"message": "Post created"})
    else:
        logger.warning(
            "Unable to create update post for club",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "chapter": update_data.chapter,
                "action": "create_update_post_club",
            },
        )
        raise HTTPException(status_code=404, detail="Error creating post")


@router.get("/{book_club_id}/feed", name="bookclub:get_feed")
async def get_club_feed(
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    filter: Optional[bool] = True,
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
    skip: Optional[int] = 0,
    limit: Optional[int] = 10,
    post_id: Optional[str] = Query(
        None,
        description="to grab an individual post"
    )
) -> List[Any]:
    """
        Gets the feed for a specific book club

    Args:
        book_club_id: The id for the book club
        filter (bool): Whether or not to filter out updates ahead of the current
            chapter for the current user. Defaults to True

    Returns:
        posts: A list of posts in chronological order, posts can only be updates.
        A post object will contain:
            id: the uuid of the post
            headline (str | None): the headline for the post
            created_date (datetime): the created datetime for the post
            chapter (int): the chapter for the post
            response (str | None): the response for the post
            user_id (str): the id of the user who made the post
            user_username (str): the username of the user who made the post
            likes (int) the number of likes on a post
            num_comments (int) the number of comments on a post
            liked_by_current_user (bool): whether the post was liked by the
                current user
            posted_by_current_user (bool): whether the post was posted by the
                current user
            type (str): the type of the post. As of now can be one of update
                and update_no_text
            awards (array): an array of awards for the post. Each award object
                will contain:
                id (str): the uuid of the award
                name (str): the name of the award
                type (str): the type of the award
                description (str): the description of the award
                num_grants (int): the number of grants for the award
    """
    print(post_id)
    posts = book_club_repo.get_book_club_feed(
        book_club_id=book_club_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        filter=filter,
        post_id=post_id,
    )
    print(posts)
    logger.info(
        "Fetched club feed",
        extra={
            "user_id": current_user.id,
            "book_club_id": book_club_id,
            "num_posts": len(posts) if isinstance(posts, list) else 1,
            "action": "get_club_feed",
        },
    )
    return JSONResponse(status_code=200, content={"posts": jsonable_encoder(posts)})


@router.delete("/{book_club_id}/remove_member", name="bookclub:remove_member_from_book_club")
async def remove_member_from_book_club(
    book_club_id: str,
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> None:
    """
    For owners of a book_club, allow them to remove members of their book_club.
    Args: 
        request: A request object that contains the following fields:
            user_id (str): the id of a user who is going to be removed from club.
        
    Returns:
        200 response

    Raises:
        400 if user is not the club admin
    """

    data = await request.json()
    try:
        member_id_to_remove = UserId(id=data.get('user_id'))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
   
    # try:
    deleted_relationship_count = book_club_repo.delete_member_from_book_club(
        current_user_id=current_user.id, 
        member_id_to_remove=member_id_to_remove.id,
        book_club_id=book_club_id,        
    )
    if deleted_relationship_count:
        logger.info(
            "Removed member from book club",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "member_id": member_id_to_remove.id,
                "action": "remove_member_from_book_club",
            },
        )
        return JSONResponse(
            status_code=200, content={"content": "member removed"}
        )
    else:
        logger.warning(
            "Unable to remove member from book club",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "member_id": member_id_to_remove.id,
                "action": "remove_member_from_book_club",
            },
        )
        raise HTTPException(status_code=401, detail='Unauthorized')
        
    # except:
    #     raise HTTPException(status_code=400, detail='Something STRANGE just happened, we are looking into it on our end.')


### Currently Reading Settings Page ########################################################################################

@router.get("/{book_club_id}/currently_reading", name="bookclub:get_currently_reading")
async def get_currently_reading(
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
):
    """
    Grabs the currently reading book for a book club
    Args: 
        book_club_id: The id of the book club
        
    Returns:
        currently_reading_book: The currently reading book for the book club

    Raises:
        400 if user is not the club member
    """

    currently_reading_book = book_club_repo.get_currently_reading_book_or_none(
        user_id=current_user.id,
        book_club_id=book_club_id,
    )

    if currently_reading_book == "No book club found":
        logger.warning(
            "Book club not found or user is not a member of the club",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "action": "get_currently_reading",
            },
        )
        raise HTTPException(status_code=400, detail="User is not a member of the club")
    
    return JSONResponse(status_code=200, content={"currently_reading_book": jsonable_encoder(currently_reading_book)})
    
@router.post("/{book_club_id}/currently_reading/start", name="bookclub:start_book")
async def start_book_for_club(
    book_club_id: str,
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    background_tasks: BackgroundTasks,
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
    book_repo: BookCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookCRUDRepositoryGraph)
    ),
) -> None:
    """
    Sets a clubs currently reading book. Does not execute if book club
    is already reading a book.

    Args:
        book_club_id: The id of the book club
        request: A request object that contains the following values:
            expected_finish_date (datetime): The date selected as the expected finish date
            book (dict): A book object that contains the following values:
                id (str): The id of the book
                chapters (int): The number of chapters in the book

    Returns:
        200 response

    Raises:
        400 if user is not the club admin
    """

    data = await request.json()

    try:
        expected_finish_datetime = datetime.fromisoformat(data.get("expected_finish_date"))
        if expected_finish_datetime.tzinfo is None:
            expected_finish_datetime = expected_finish_datetime.replace(tzinfo=timezone.utc)

        start_currently_reading = BookClubSchemas.StartCurrentlyReading(
            expected_finish_date=expected_finish_datetime,
            book=data.get("book"),
            user_id=current_user.id,
            id=book_club_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not start_currently_reading.book.get(
        "id"
    ) or not start_currently_reading.book.get("chapters"):
        logger.warning(
            "Missing required value",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "action": "start_book_for_club",
            },
        )
        raise HTTPException(status_code=400, detail="Missing required value")

    book_exists = True
    if start_currently_reading.book["id"][0] == "g":
        book_exists = False
        canonical_book = book_repo.get_canonical_book_by_google_id_extended(
            start_currently_reading.book["id"]
        )
        if canonical_book:
            book_exists = True
            start_currently_reading.book['id'] = canonical_book.id
            start_currently_reading.book['chapters'] = start_currently_reading.book["chapters"]

    if book_exists:
        result = book_club_repo.create_currently_reading_club(start_currently_reading)
    else:
        google_book = google_books_pull.pull_google_book(
            start_currently_reading.book["id"], book_repo
        )
        result = book_club_repo.create_currently_reading_club_and_book(
            start_currently_reading,
            google_book.title,
            google_book.small_img_url,
            google_book.author_names,
        )

        if result:
            background_tasks.add_task(
                google_books_background_tasks.update_book_google_id,
                start_currently_reading.book["id"],
                book_repo,
            )

    if result:
        logger.info(
            "Started book for club",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "book_id": start_currently_reading.book["id"],
                "action": "start_book_for_club",
            },
        )
        return JSONResponse(
            status_code=200, 
            content={
                "message": "Book set as currently reading",
                "book_club_book_id": result
                }
        )
    else:
        logger.warning(
            "Unable to start book for club",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "book_id": start_currently_reading.book["id"],
                "action": "start_book_for_club",
            },
        )
        raise HTTPException(status_code=400, detail="Error starting book")


@router.post("/{book_club_id}/currently_reading/finish", name="bookclub:finish_book")
async def finish_book_for_club(
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> None:
    """
    Set the currently reading book as finished

    Args:
        book_club_id: The id of the book club

    Returns:
        200 response

    Raises:
        400 if current user is not the club admin
    """
    result = book_club_repo.update_finished_reading(book_club_id, current_user.id)

    if result:
        logger.info(
            "Finished book for club",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "action": "finish_book_for_club",
            },
        )
        return JSONResponse(
            status_code=200, content={"message": "Book set as finished reading"}
        )
    else:
        logger.warning(
            "Unable to finish book for club",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "action": "finish_book_for_club",
            },
        )
        raise HTTPException(status_code=400, detail="Error finishing book")


@router.post("/{book_club_id}/currently_reading/stop", name="bookclub:stop_book")
async def stop_book_for_club(
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> None:
    """
    Set the currently reading book as quit

    Args:
        book_club_id: The id of the book club

    Returns:
        200 response

    Raises:
        400 if current user is not the club admin
    """
    result = book_club_repo.update_stopped_reading(book_club_id, current_user.id)

    if result:
        logger.info(
            "Stopped book for club",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "action": "stop_book_for_club",
            },
        )
        return JSONResponse(
            status_code=200, content={"message": "Book set as stopped reading"}
        )
    else:
        logger.warning(
            "Unable to stop book for club",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "action": "stop_book_for_club",
            },
        )
        raise HTTPException(status_code=404, detail="Error finishing book")


@router.get("/{book_club_id}/club_invites", name="bookclub:invites_for_club")
async def invites_for_bookclub(
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> None:
    """
    gets all outstanding invites for an admins view of bookclub members setting
    """

    invites = book_club_repo.get_invites_for_book_club(
        book_club_id=book_club_id, user_id=current_user.id
    )
    
    logger.info(
        "Fetched invites for book club",
        extra={
            "user_id": current_user.id,
            "book_club_id": book_club_id,
            "num_invites": len(invites),
            "action": "invites_for_bookclub",
        },
    )

    return JSONResponse(
        status_code=200, content={"invites": jsonable_encoder(invites)}
    )
    


### AWARDS ENDPOINTS #######################
@router.get("/{book_club_id}/awards", name="bookclub:get_awards")
async def get_awards(
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    current_uses: Optional[bool] = False,
    post_id: Optional[str] = None,
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> Any:
    """
    Gets all the awards available for the current book
    in a club. Optionally it can return the number of
    times this user has used the award, the total number
    of times the user can use the award, and the number of times
    the award has been applied to a post and by which users

    Args:
        book_club_id: (str) the book club id
        current_uses: (optional, bool) whether to include
                the number of times the user has used the award this book
        post_id: (optional,str) The post id. returns the data related to
                how many times this award has been granted to the post

    Returns:
        awards: a list that contains the following object
            award: a dictionary that contains the following fields
                id: (str) the id of the award
                name: (str) the name of the award
                type: (str) the type of award
                description: (str) description for the award
                allowed_uses: (int) the number of
                    times this award can be granted per book
                current_uses: (int) if included as flag, the number of
                    times this award has been used for the current book
                grants: if the post_id is included, this is a list that contains
                    the following grant objects
                        granted_date (datetime) the date the award was granted
                        user: a user object that contains the following data
                            id: the id of the user that granted the award
                            username: the username of the user that granted the
                                award
    """
    if post_id:
        awards = book_club_repo.get_awards_with_grants(
            book_club_id,
            current_user.id,
            current_uses,
            post_id
        )
    else:
        awards = book_club_repo.get_awards(
            book_club_id,
            current_user.id,
            current_uses
        )

    logger.info(
        "Fetched awards for book club",
        extra={
            "user_id": current_user.id,
            "book_club_id": book_club_id,
            "num_awards": len(awards),
            "action": "get_awards",
        },
    )

    return JSONResponse(
        status_code=200, content={"awards": jsonable_encoder(awards)}
    )

@router.put(
    "/{book_club_id}/post/{post_id}/award/{award_id}", name="bookclub:put_award"
)
async def put_award(
    book_club_id: str,
    post_id: str,
    award_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> None:
    """
    Attaches an award to a post in a club

    Args:
        book_club_id: (str) the book club id
        post_id: (str) the id of the post
        award_id: (str) the id of the award

    Returns:
        200 status code if awards is attached

    Raises:
        401 if not proper permissions
        403 if the user has no awards left to grant
    """

    try:
        create_award = BookClubSchemas.CreateAward(
            post_id=post_id,
            award_id=award_id,
            user_id=current_user.id,
            book_club_id=book_club_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    response = book_club_repo.create_award_for_post(
        create_award
    )

    if response == "award created":
        logger.info(
            "Award added to post",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "post_id": post_id,
                "award_id": award_id,
                "action": "put_award",
            },
        )
        return JSONResponse(
        status_code=200, content={"message": "award added"}
        )
    elif response == "unauthorized":
        logger.warning(
            "Unauthorized to add award to post",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "post_id": post_id,
                "award_id": award_id,
                "action": "put_award",
            },
        )
        raise HTTPException(status_code=401, detail="unauthorized")
    else:
        logger.warning(
            "Maximum number of grants reached",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "post_id": post_id,
                "award_id": award_id,
                "action": "put_award",
            },
        )
        raise HTTPException(
            status_code=403, 
            detail="maximum number of grants reached")


@router.delete(
    "/{book_club_id}/post/{post_id}/award/{award_id}", name="bookclub:delete_award"
)
async def delete_award(
    book_club_id: str,
    post_id: str,
    award_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
) -> None:
    """
    Removes an award from a post in a club

    Args:
        book_club_id: (str) the book club id
        post_id: (str) the id of the post
        award_id: (str) the id of the award. This can be a granted award or
            the general award.

    Returns:
        200 status code if award is removed

    Raises:
        404 if award not found
    """

    try:
        delete_award = BookClubSchemas.DeleteAward(
            post_id=post_id,
            award_id=award_id,
            user_id=current_user.id,
            book_club_id=book_club_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

    if award_id.startswith("post_award_"):
        response = book_club_repo.delete_award_for_post_by_id(
            delete_award
        )
    else:
        response = book_club_repo.delete_award_for_post(
            delete_award
        )

    if response:
        logger.info(
            "Award deleted from post",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "post_id": post_id,
                "award_id": award_id,
                "action": "delete_award",
            },
        )
        return JSONResponse(
        status_code=200, content={"message": "award deleted"}
        )
    else:
        logger.warning(
            "Award not found",
            extra={
                "user_id": current_user.id,
                "book_club_id": book_club_id,
                "post_id": post_id,
                "award_id": award_id,
                "action": "delete_award",
            },
        )
        raise HTTPException(
            status_code=404, 
            detail="award not found")

@router.get("/{book_club_id}/preview_emails/{email_type}", name='bookclubs:test_emails')
async def test_emails(
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
    email_type: str = 'invite',
):  
    to_email = 'test@hardcoverlit.com'
    invite_id = '🍕'

    # ONlY MICHAEL CAN VIEW FOR NOW? 
    if current_user.id != 'a0f86d40-4915-4773-8aa1-844d1bfd0b41':
        return HTTPException(status_code=400, detail='YOU CANT DO THAT BECAUSE YOU ARENT MICHAEL OR KYLE')
    
    # Maybe think about other places we want to test this shit?
    if email_type == 'invite':
        preview_email = email_client.send_invite_email(
                to_email=to_email,
                invite_id=invite_id,
                book_club_id=book_club_id,
                invite_user_username=current_user.username,
                subject="Someone Invited You to Join a Book Club!",
                book_club_repo=book_club_repo,
                is_debug=True
        )
        return JSONResponse(status_code=200, content={'email': jsonable_encoder(preview_email)})
    
# CLUB NOTIFICATIONS
# Annoy your friends to finish reading their books.
@router.post("/{book_club_id}/create_notification", name='bookclubs:create_notification')
async def create_club_notification(
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: Request,
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
):
    """
    Allow club members to peer pressure each other into reading more if the club / user allows it.
    """
    data = await request.json()

    try:
        notif = BookClubSchemas.ClubNotificationCreate(
            member_id=data.get('member_id'),
            notification_type=data.get('notification_type'),
            sent_by_user_id=current_user.id,
            book_club_id=book_club_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    eligible = book_club_repo.get_notification_eligibility(notif)
    if not eligible:
        raise HTTPException(status_code=400, detail='User is not eligible to send that notification.')
    
    notification = book_club_repo.create_club_notification(
        notif
    )

    if notification:
        return JSONResponse(status_code=200, content={'notification': jsonable_encoder(notification)})
    else:
        raise HTTPException(status_code=400, detail='Missing member_id and notification_type from request payload.')

@router.get("/notifications_for_clubs/{user_id}", name="bookclubs:get_notifications")
async def get_notifications_for_member_clubs(
    user_id: str, 
    current_user: Annotated[User, Depends(get_current_active_user)], 
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    )
):
    """
    Get paginated notifications for a user that have not been dismissed and are still relevant to the current book. 
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail='Unauthorized dude')
    
    notifications = book_club_repo.get_notifications_for_user_by_club(
        user_id=user_id,
    )

    return JSONResponse(status_code=200, content={'notifications': jsonable_encoder(notifications)})


@router.put("/dismiss_notification/{notification_id}", name="bookclubs:dismiss_notification")
async def update_club_notification_to_dismiss(
    notification_id:str,
    current_user: Annotated[User, Depends(get_current_active_user)], 
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
):
    """
    Sets a notification as dismissed and returns a string indicating whether or not you did
    """

    is_dismissed = book_club_repo.update_club_notification_to_dismissed(
        member_id=current_user.id,
        notification_id=notification_id,
    )
    
    if is_dismissed:
        detail = f'dismissed {notification_id}'
        return JSONResponse(status_code=200, content={'success': detail})
    else:
        detail = f'failed to dismiss {notification_id}'
        raise HTTPException(status_code=400, detail=detail)



## Create review for book club

@router.post("/{book_club_id}/review/create/{book_club_book_id}", name='bookclubs:create_review')
async def create_review_for_user(
    book_club_id: str,
    book_club_book_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: Request,
    background_tasks: BackgroundTasks, 
    no_review: Optional[bool] = False,
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
):
    """
    Creates the final review for the currently reading book and
    sets the book as finished for the user.

    Also creates a background task to notify other club
    members that someone has finished the book. 

    Args:
        no_review (Optional(book)): A boolean that is true if the user
            does not want to write a review. A rating can still
            be provided.
        request: A request object that contains the following fields:
            user (dict): A user object containing the following fields:
                id (str): The id of the user
            questions (list | None): The questions the user included in to post
            ids (list | None): The ids of questions the user included in the post
            rating: int | None = None: The rating the user gave the book
            responses (list | None): The responses for the questions
            headline (str): The headline for the post

    Returns:
        200 response for a successful post
    """
    data = await request.json()
    
    user_id = data.get("user",{}).get("id")
    if user_id != current_user.id:
        raise HTTPException(400, "Unauthorized")

    if not no_review:
        try:
            review = BookClubSchemas.CreateReviewPost(
                user = {
                    "id": user_id
                },
                headline=data.get("headline"),
                questions=data.get("questions"),
                question_ids=data.get("ids"),
                responses=data.get("responses"),
                rating=data.get("rating"),
                id=book_club_id,
                book_club_book_id= book_club_book_id
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        response = book_club_repo.create_review_and_finished_reading(
            review
        )

        if response:
            #TODO: Add background task to notify users

            return JSONResponse(
                status_code=200,
                content={
                    "message": "Review Created"
                }
            )
        
        else:
            raise HTTPException(400, "Error creating review")
    
    else:
        try:
            review = BookClubSchemas.CreateReviewPostNoText(
                rating=data.get("rating"),
                book_club_book_id=book_club_book_id
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        response = book_club_repo.create_finished_reading(
            user_id,
            book_club_id,
            review.rating,
            review.book_club_book_id
        )

        if response:
            #TODO: Add background task to notify users

            return JSONResponse(
                status_code=200,
                content={
                    "message": "Book finished"
                }
            )
        
        else:
            raise HTTPException(400, "Error creating review")

@router.get("/{book_club_id}/feed/finished", name='bookclubs:get_finished_feed')
async def get_finished_feed(
    book_club_id:str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    ),
    skip: Optional[int] = 0,
    limit: Optional[int] = 10,
) -> List[Any]:
    """
    Gets a version of the feed that includes review posts for finished
    readers. I think its probably better to add this as a flag to the
    get_club_feed endpoint. We could also just have the normal feed endpoint
    check if the user if finished and update how it returns

    Args:
        book_club_id: The id for the book club

    Returns:
        posts: A list of posts in chronological order, posts can only be updates
        and reviews.
        A post object will contain:
            id: the uuid of the post
            headline (str | None): the headline for the post
            created_date (datetime): the created datetime for the post
            chapter (int): the chapter for the post
            response (str | None): the response for the post
            user_id (str): the id of the user who made the post
            user_username (str): the username of the user who made the post
            likes (int) the number of likes on a post
            num_comments (int) the number of comments on a post
            liked_by_current_user (bool): whether the post was liked by the
                current user
            posted_by_current_user (bool): whether the post was posted by the
                current user
            type (str): the type of the post. As of now can be one of update
                and update_no_text
            awards (array): an array of awards for the post. Each award object
                will contain:
                id (str): the uuid of the award
                name (str): the name of the award
                type (str): the type of the award
                description (str): the description of the award
                num_grants (int): the number of grants for the award
    """
    posts = book_club_repo.get_book_club_finished_feed(
        book_club_id=book_club_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    logger.info(
        "Fetched club finished feed",
        extra={
            "user_id": current_user.id,
            "book_club_id": book_club_id,
            "num_posts": len(posts),
            "action": "get_club_finished_feed",
        },
    )
    return JSONResponse(status_code=200, content={"posts":jsonable_encoder(posts)})

@router.get(
    "/{book_club_id}/afterword/{user_id}/user_stats/{book_club_book_id}", 
    name='bookclubs:get_afterword_user_stats'
    )
async def get_afterword_user_stats(
    book_club_id: str,
    user_id:str,
    book_club_book_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    )
):
    """
    Gets the first page of the afterword for a user in a book club.
    This includes their stats including:
        - The number of days they took
        - The number of updates they wrote
        - The number of awards they granted
    
    Maybe we should have some additional incase and of these stats are
    empty. Some options would be:
        - The number of comments they wrote
        - The number of posts they liked

    Args:
        book_club_id (str): The id for the book club they are getting the afterword for
        user_id (str): The id of the user
        book_club_book_id (str): The id for the BookClubBook node that this
            afterword is being created for

    Returns: 
        stats (dict): This is a json object that contains:
            days (int): The number of days they took to read the book
            updates (int): The number of updates they wrote
            awards (int): The number of awards they granted
    """
    if current_user.id != user_id:
        logger.warning(
            "Unauthorized User",
            extra={
                "current_user_id": current_user.id,
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_user_stats",
            },
        )
        raise HTTPException(401, "Unauthorized")
    
    stats = book_club_repo.get_afterward_user_stats(
        book_club_id,
        book_club_book_id,
        user_id,
    )
    
    if stats:
        logger.info(
            "Retrieved afterword user stats",
            extra={
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_user_stats"
            }
        )
        return JSONResponse(
            status_code=200,
            content={
                "stats": stats
            }
        )
    else:
        logger.warning(
            "Error grabbing user stats",
            extra={
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_user_stats"
            }
        )
        raise HTTPException(
            status_code=400,
            detail="Unable to grab user stats"
        )
        
    

@router.get(
    "/{book_club_id}/afterword/{user_id}/friend_thoughts/{book_club_book_id}", 
    name='bookclubs:get_afterword_friend_thoughts'
    )
async def get_afterword_friend_thoughts(
    book_club_id: str,
    user_id: str,
    book_club_book_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookClubCRUDRepositoryGraph)
    )
):
    """
    Gets the second page of the afterword for a user in a book club.
    This page includes the headline from each readers review if they posted one,
    and their rating of the book.

    NOTE: What to do if no one has posted anything?
        Might not be worth handling yet

    Args:
        book_club_id (str): The id for the book club they are getting the afterword for
        user_id (str): The id of the user
        book_club_book_id (str): The id for the BookClubBook node that this
            afterword is being created for

    Returns: 
        thoughts (list): This is an array that contains:
            user (dict): the user who the thought belongs to. A dict with:
                id (str): The id for the user
                username (str): The username for the user
                is_current_user (bool): Whether the user is the current user
            review (dict): Review related information. A dict including:
                headline (str): The headline for the review
                rating (int): The rating the user gave the book

        NOTE: Haven't yet decided how these are sorted
    """
    if current_user.id != user_id:
        logger.warning(
            "Unauthorized User",
            extra={
                "current_user_id": current_user.id,
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_friend_thoughts",
            },
        )
        raise HTTPException(401, "Unauthorized")
    
    friend_thoughts = book_club_repo.get_afterward_friend_thoughts(
        book_club_id,
        book_club_book_id,
        user_id
    )
    
    if friend_thoughts:
        logger.info(
            "Retrieved afterword friend thoughts",
            extra={
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_friend_thoughts"
            }
        )
        return JSONResponse(
            status_code=200,
            content={
                "friend_thoughts": friend_thoughts
            }
        )
    else:
        logger.warning(
            "Error grabbing friend thoughts",
            extra={
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_friend_thoughts"
            }
        )
        raise HTTPException(
            status_code=400,
            detail="Unable to grab friend thoughts"
        )

@router.get(
    "/{book_club_id}/afterword/{user_id}/consensus/{book_club_book_id}", 
    name='bookclubs:get_afterword_consensus'
    )
async def get_afterword_consensus(
    book_club_id: str,
    user_id: str,
    book_club_book_id: str,
    current_user: Annotated[User,Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(BookClubCRUDRepositoryGraph)
    )
):
    """
    Gets the third page. This is the consensus thoughts from the group. 
    This includes the ratings of every member, including the current user. 
    As well as a general consensus.

    Args:
        book_club_id (str): The id for the book club they are getting the afterword for
        user_id (str): The id of the user
        book_club_book_id (str): The id for the BookClubBook node that this
            afterword is being created for
    
    Returns: 
        consensus (dict): This is an object that contains:
            loved (array): An array of the users that loved the book. This contains:
                user (dict): The information about the user:
                    id (str): The user id
                    username (str): The username
            liked (array):  An array of the users that liked the book. This contains
                the same as loved
            disliked (array):  An array of the users that disliked the book. This contains
                the same as loved
            group_consensus (dict): A dictionary with the following:
                majority (str): The majority choice for the group (loved, liked, or disliked)
                user_agreed_with_majority (bool): Whether or not the user agreed with the majority
                num_times_result (int): The number of times the user_agreed_with_majority
                    result has happened. Ex. "The user has (agreed/disagreed) n times"
    """
    if current_user.id != user_id:
        logger.warning(
            "Unauthorized User",
            extra={
                "current_user_id": current_user.id,
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_consensus",
            },
        )
        raise HTTPException(401,"Unauthorized")
    
    consensus = book_club_repo.get_afterward_consensus(
        book_club_id,
        book_club_book_id,
        user_id
    )
    
    if consensus:
        logger.info(
            "Retrieved afterword consensus",
            extra={
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_consensus"
            }
        )
        return JSONResponse(
            status_code=200,
            content={
                "consensus": consensus
            }
        )
    else:
        logger.warning(
            "Error grabbing consensus",
            extra={
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_consensus"
            }
        )
        raise HTTPException(
            400,
            "Unable to grab consensus"
        )

@router.get(
    "/{book_club_id}/afterword/{user_id}/highlights/{book_club_book_id}", 
    name='bookclubs:get_afterword_highlights'
    )
async def get_afterword_highlights(
    book_club_id: str,
    user_id: str,
    book_club_book_id: str,
    current_user: Annotated[User,Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(BookClubCRUDRepositoryGraph)
    )
):
    """
    This is the fourth page.
    Gets the highlights from this book for the user. This includes:
        - Most controversial update
        - Most agreed with update

    Args:
        book_club_id (str): The id for the book club they are getting the afterword for
        user_id (str): The id of the user
        book_club_book_id (str): The id for the BookClubBook node that this
            afterword is being created for

    Returns: 
        highlights (dict): An object containing
            controversial_post (dict): A post object containing:
                id: the uuid of the post
                headline (str | None): the headline for the post
                created_date (datetime): the created datetime for the post
                chapter (int): the chapter for the post
                response (str | None): the response for the post
                likes (int): the number of likes on a post
                awards (dict): an array of awards for the post. Each award object
                will contain:
                    id (key, str): the uuid of the award
                    name (str): the name of the award
                    type (str): the type of the award
                    description (str): the description of the award
                    num_grants (int): the number of grants for the award
            agreed_post (dict): A post object

    NOTE: Need to think about edge cases here for:
        User made no updates
        Overlap from one post into multiple highlights
            Ex. Same post is the most agreed with and most controversial
    """
    if current_user.id != user_id:
        logger.warning(
            "Unauthorized User",
            extra={
                "current_user_id": current_user.id,
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_highlights",
            },
        )
        raise HTTPException(401,"Unauthorized")
    
    highlights = book_club_repo.get_afterward_highlights(
        book_club_id,
        book_club_book_id,
        user_id
    )
    
    if highlights:
        logger.info(
            "Retrieved afterword highlights",
            extra={
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_highlights"
            }
        )
        return JSONResponse(
            status_code=200,
            content={
                "highlights": jsonable_encoder(highlights)
            }
        )
    else:
        logger.warning(
            "Error grabbing highlights",
            extra={
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_highlights"
            }
        )
        raise HTTPException(
            400,
            "Unable to grab highlights"
        )

@router.get(
    "/{book_club_id}/afterword/{user_id}/club_stats/{book_club_book_id}"
    , name='bookclubs:get_club_reading_status'
    )
async def get_club_reading_status(
    book_club_id: str,
    user_id: str,
    book_club_book_id: str,
    current_user: Annotated[User,Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(BookClubCRUDRepositoryGraph)
    )
):
    """
    This is the 5th page.
    Gets stats from the clubs reading. This includes:
        Data for line graph of reading history

    Args:
        book_club_id (str): The id for the book club they are getting the afterword for
        user_id (str): The id of the user
        book_club_book_id (str): The id for the BookClubBook node that this
            afterword is being created for

    Returns: 
        reading_history (array): An array of each user's reading progress. 
            Each object in the array contains a dictionary with:
                user (dict): the data for the user this object is about,
                    this contains:
                        id (str): The user id
                        username (str): The user username
                progress_over_time (array): An array of the users progress over time,
                    Each object in the array contains a dictionary with:
                        timestamp (datetime): The datetime of the progress
                        chapter (int): The chapter the progress is associated with

        Here is an example return:
            {
                "reading_history": [
                    {
                        "user": {
                            "id":"user123",
                            "username": "Alice",
                        },
                        "progress_over_time": [
                            {"timestamp": "2025-01-01T10:00:00Z", "chapter": 10},
                            {"timestamp": "2025-01-02T10:00:00Z", "chapter": 25},
                            {"timestamp": "2025-01-03T10:00:00Z", "chapter": 50}
                        ]
                    },
                    {
                        "user": {
                            "id":"user456",
                            "username": "Bob",
                        },
                        "progress_over_time": [
                            {"timestamp": "2025-01-01T10:00:00Z", "chapter": 5},
                            {"timestamp": "2025-01-02T10:00:00Z", "chapter": 20},
                            {"timestamp": "2025-01-03T10:00:00Z", "chapter": 30}
                        ]
                    }
                ]
                }
    """
    if current_user.id != user_id:
        logger.warning(
            "Unauthorized User",
            extra={
                "current_user_id": current_user.id,
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_club_stats",
            },
        )
        raise HTTPException(401,"Unauthorized")
    
    club_stats = book_club_repo.get_afterward_club_stats(
        book_club_id,
        book_club_book_id,
        user_id
    )
    
    if club_stats:
        logger.info(
            "Retrieved afterword club stats",
            extra={
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_club_stats"
            }
        )
        return JSONResponse(
            status_code=200,
            content={
                "club_stats": jsonable_encoder(club_stats)
            }
        )
    else:
        logger.warning(
            "Error grabbing club stats",
            extra={
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_club_stats"
            }
        )
        raise HTTPException(
            400,
            "Unable to grab club stats"
        )
    
@router.get(
    "/{book_club_id}/afterword/{user_id}/award_stats/{book_club_book_id}"
    , name='bookclubs:get_afterword_club_stats'
    )
async def get_afterword_award_stats(
    book_club_id: str,
    user_id: str,
    book_club_book_id: str,
    current_user: Annotated[User,Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(BookClubCRUDRepositoryGraph)
    )
):
    """
    This is the 5th page.
    Gets stats from the clubs reading. This includes:
        Data for table of awards granted to each user

    Args:
        book_club_id (str): The id for the book club they are getting the afterword for
        user_id (str): The id of the user
        book_club_book_id (str): The id for the BookClubBook node that this
            afterword is being created for

    Returns: 
        users_table (array): An array of each user's award stats. 
            Each object in the array contains a dictionary with:
                user (dict): the data for the user this object is about,
                    this contains:
                        id (str): The user id
                        username (str): The user username
                award_counts (array): An array of the users awards received for this book,
                    Each object in the array contains a dictionary with:
                        id (str): The id for the award
                        name (str): The name of the award
                        type (str): The type of the award
                        description (str): The description for the award
                        count (int): The number of times the award was granted
        awards (dict): All of the awards for this club. This contains
            id (key, str): The award id
            name (str): The name of the award
            description (str): The description for the award
            type (str): The type of the award
            cls (str): The class of the award


        Here is an example of the return object:

        {
            "users_table": [
                {
                "user": {
                    "id":"user123",
                    "username": "Alice",
                }
                "award_counts": [
                    {
                    "id": "award1",
                    "count": 10
                    },
                    {
                    "id": "award2",
                    "count": 3
                    }
                ]
                },
                {
                "user": {
                    "id":"user456",
                    "username": "Bob",
                }
                "award_counts": [
                    {
                    "id": "award1",
                    "count": 1
                    },
                    {
                    "id": "award2",
                    "count": 4
                    }
                ]
                },
            ],
        "awards": {
            "award1": {
                "name": "Commendable",
                "type": "Positive",
                "description": "Given for outstanding contributions.",
                "cls": "class"
            },
            "award2": {
                "name": "Questionable",
                "type": "Negative",
                "description": "Given for dubious contributions.",
                "cls": "class"
            }
}

    """
    if current_user.id != user_id:
        logger.warning(
            "Unauthorized User",
            extra={
                "current_user_id": current_user.id,
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_award_stats",
            },
        )
        raise HTTPException(401,"Unauthorized")
    
    award_stats = book_club_repo.get_afterward_award_stats(
        book_club_id,
        book_club_book_id,
        user_id
    )
    
    if award_stats:
        logger.info(
            "Retrieved afterword award stats",
            extra={
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_award_stats"
            }
        )
        return JSONResponse(
            status_code=200,
            content={
                "award_stats": jsonable_encoder(award_stats)
            }
        )
    else:
        logger.warning(
            "Error grabbing award stats",
            extra={
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "get_afterword_award_stats"
            }
        )
        raise HTTPException(
            400,
            "Unable to grab award stats"
        )
    
@router.put(
"/{book_club_id}/afterword/{user_id}/mark_as_viewed/{book_club_book_id}"
, name='bookclubs:set_afterword_as_viewed'
)
async def set_afterword_as_viewed(
    book_club_id: str,
    user_id: str,
    book_club_book_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(BookClubCRUDRepositoryGraph)
    )
):
    """
    Marked the afterword as viewed for a specific reader

    Args:
        book_club_id (str): The id for the book club they are getting the afterword for
        user_id (str): The id of the user
        book_club_book_id (str): The id for the BookClubBook node that this
            afterword is being created for

    Returns: 
        200: If status is successfully updated
    """
    if current_user.id != user_id:
        logger.warning(
            "Unauthorized User",
            extra={
                "current_user_id": current_user.id,
                "user_id": user_id,
                "book_club_id": book_club_id,
                "action": "set_afterword_as_viewed",
            },
        )
        raise HTTPException(401,"Unauthorized")
    
    status = book_club_repo.updated_afterword_to_viewed(
        book_club_id,
        book_club_book_id,
        user_id
    )

    if status:
        return JSONResponse(
            status_code=200,
            content={"content": "Status updated"}
        )
    else:
        raise HTTPException(
            status_code=403,
            detail="Unknown error updating status"
        )
    
@router.get(
    "/{book_club_id}/check_status",
    name='bookclubs:get_afterword_club_stats'
)
async def get_afterword_award_stats(
    book_club_id: str,
    current_user: Annotated[User,Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = Depends(
        get_repository(BookClubCRUDRepositoryGraph)
    )
):
    """
    Checks for multiple flags that determine UX for bookclubs

    Args:
        book_club_id: The id of the book club
        current_user: The current user
        book_club_repo: The repo for the book club CRUD operations

    Returns:
        is_member (bool): 
        is_owner
        is_user_finished_with_current_book
        is_club_finished_with_current_book
        has_viewed_afterword
    """
    is_member, is_owner = book_club_repo.get_member_status_book_club(
        book_club_id,
        current_user.id
    )

    if is_member:
        response = book_club_repo.get_reading_status_book_club(
            book_club_id,
            current_user.id
        )

        is_user_finished_with_current_book = response[0]
        is_club_finished_with_current_book = response[1]
        has_viewed_afterword = response[2]
    else:
        is_user_finished_with_current_book = None
        is_club_finished_with_current_book = None
        has_viewed_afterword = None

    return JSONResponse(
            status_code=200,
            content={
                "data": {
                    "is_member":is_member,  
                    "is_owner":is_owner,
                    "is_user_finished_with_current_book":is_user_finished_with_current_book,
                    "is_club_finished_with_current_book":is_club_finished_with_current_book,
                    "has_viewed_afterword":has_viewed_afterword
                }
            }
    )


# TODO:
"""
- Update minimal preview to include the users status.
    - {
    "is_member"
    "is_user_finished_with_current_book"
    "is_club_finished_with_current_book"
    "has_viewed_afterword"
    }
- Add notifications to the marked as finished endpoint so users know wrapped is available
- Should all of the afterword endpoints confirm the book is finished first? Probably

"""


# TODO: implement some WS connection manager for members of a bookclub 
# so they can find where someone is on a post, to be able to have some sense of 
# where the conversation is happening while you are on the app.
"""
@router.websocket("/ws/{bookclub_id}/thread")
async def bookshelf_connection(
    websocket: WebSocket,
    bookshelf_id: str,
    token: str = Query(...),
    bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookshelfCRUDRepositoryGraph)
    ),
    user_repo: UserCRUDRepositoryGraph = Depends(
        get_repository(repo_type=UserCRUDRepositoryGraph)
    ),
    book_repo: BookCRUDRepositoryGraph = Depends(
        get_repository(repo_type=BookCRUDRepositoryGraph)
    ),
):
    try:
        current_user = await get_bookclub_websocket_user(token=token)
        print("entered bookshelf_connection")
    except:
        logger.warning(
            "Failed to authenticate user for bookshelf websocket",
            extra={
                "bookshelf_id": bookshelf_id
            }
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if current_user.bookshelf_id != bookshelf_id:
        logger.warning(
            "Bookshelf id does not match id from token",
            extra={
                "bookshelf_id": bookshelf_id,
                "token_bookshelf_id": current_user.bookshelf_id
            }
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if bookclub_id not in bookclub_ws_manager.cache:
        logger.warning(
            "Bookshelf not  in cache",
            extra={
                "bookshelf_id": bookshelf_id
            }
        )
        # THIS NEEDS TO REDIRECT TO THE /api/bookshelves/{bookshelf_id} endpoint
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if current_user.id not in bookclub_ws_manager.cache[bookshelf_id].contributors:
        logger.warning(
            "User is not authorized to connect to this bookshelf",
            extra={
                "user_id": current_user.id,
                "bookshelf_id": bookshelf_id
            }
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    await bookclub_ws_manager.connect(bookshelf_id, current_user.id, websocket)

    try:
        while (
            True and bookshelf_id in bookclub_ws_manager.cache
        ):  # CAN THE TRUE BE REMOVED?
            data = await websocket.receive_json()
            background_tasks = BackgroundTasks()
            print(data)
            try:
                task = BookshelfTaskRoute(type=data["type"], token=data["token"])
            except ValueError as e:
                await bookshelf_ws_manager.invalid_data_error(bookshelf_id=bookshelf_id)
                continue

            try:
                current_user = await get_bookshelf_websocket_user(token=task.token)
            except:
                logger.warning(
                    "Failed to authenticate user for bookshelf websocket",
                    extra={
                        "bookshelf_id": bookshelf_id
                    }
                )
                await bookshelf_ws_manager.disconnect(bookshelf_id, websocket)
                return
          

            if data["type"] == "joined":
                pass

            if data["type"] == "left":
                pass
    except WebSocketDisconnect:
        await bookshelf_ws_manager.disconnect_without_close(bookshelf_id, websocket)
"""