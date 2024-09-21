from datetime import datetime
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
    
    response = book_club_repo.create_bookclub_invites_dep(invite)
    
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
    
@router.post("/invite_new",
            name="bookclub:invite_new")
async def invite_users_to_club_new(
        request: Request,
        current_user:  Annotated[User, Depends(get_current_active_user)],
        book_club_repo: BookClubCRUDRepositoryGraph = 
            Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
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

    user_ids = [invites[item].get("user_id") 
                for item in invites 
                if (invites[item].get("user_id") and 
                    invites[item].get("user_id") != current_user.id)]
    
    emails = [invites[item].get("email") 
              for item in invites 
              if invites[item].get("email") and not invites[item].get("user_id")]
    
    if not user_ids and not emails:
        raise HTTPException(
            status_code=400, 
            detail="No data sent")

    try:
        invite_obj = BookClubSchemas.BookClubInvite(
            book_club_id=data.get("book_club_id"),
            user_id=current_user.id,
            user_ids=user_ids,
            emails=emails
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    response = book_club_repo.create_bookclub_invites(invite_obj)
    
    if invite_obj.emails:
        for email in invite_obj.emails:
            if email in response:
                if response[email] != "already_member":
                    email_client.send_invite_email(
                        email, 
                        "Someone Invited You to Join a Book Club!")
                    
    for item in invites:
        invite = invites[item]
        if invite.get("user_id"):
            if not response.get(invite.get("user_id")):
                invite.update({"status":"error"})
            else:
                invite.update({
                    "status":response[invite.get("user_id")].get("status")})
                if response.get(invite.get("user_id")).get("id"):
                    invite.update({
                    "id":response[invite.get("user_id")].get("id")})
            
        elif invite.get("email"):
            if not response.get(invite.get("email")):
                invite.update({"status":"error"})
            else:
                invite.update({
                    "status":response[invite.get("email")].get("status")})
                if response.get(invite.get("email")).get("id"):
                    invite.update({
                    "id":response[invite.get("email")].get("id")})
        

    return invites

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
        return JSONResponse(
            status_code=200, 
            content={"message": "Invite declined"})

@router.get("/{book_club_id}/minimal_preview/{user_id}/user", name="bookclub:minimal_preview")
async def get_book_club_minimal_preview(
    book_club_id: str,
    user_id: str,
    current_user:  Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = 
        Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
):
    """
    gets an minimal preview for a bookclub via clubs uuid. 
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail="Unauthorized")

    try:
        book_club = book_club_repo.get_minimal_book_club(book_club_id=book_club_id, user_id=user_id)
    except:
        raise HTTPException(
            status_code=404,
            detail="Bookclub not found"
        )
    
    return JSONResponse(content={"book_club":jsonable_encoder(book_club)})
    
### Club feed page ################################################################################################

@router.get("/{book_club_id}/user_pace",
            name="bookclub:user_pace")
async def get_user_pace(
    book_club_id: str,
    current_user:  Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = 
        Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
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
        return JSONResponse(
            status_code=200, 
            content={"paces": jsonable_encoder(paces)})
    else:
        raise HTTPException(
            status_code=404, 
            detail="Invite not found")
        
@router.get("/{book_club_id}/club_members_pace",
            name="bookclub:club_members_pace")
async def get_club_members_pace(
    book_club_id: str,
    current_user:  Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = 
        Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
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

    member_paces = book_club_repo.get_member_paces(
        book_club_id,
        current_user.id)
    
    if member_paces is not None:
        return JSONResponse(
            status_code=200, 
            content={"member_paces": jsonable_encoder(member_paces)})
    else:
        raise HTTPException(
            status_code=404, 
            detail="Invite not found")

@router.post("/{book_club_id}/update/create",
             name="bookclub:update_create")
async def create_update_post_club(
    request: Request,
    book_club_id: str,
    current_user:  Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = 
        Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
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
        raise HTTPException(status_code=400, detail="User is a required field")
    
    if data.get("user").get("id") != current_user.id:
        raise HTTPException(status_code=400, detail="Unauthorized")
    
    try:
        update_data = BookClubSchemas.UpdatePost(
            user=data.get("user"),
            chapter=data.get("chapter"),
            response=data.get("response"),
            headline=data.get("headline"),
            id=book_club_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if update_data.get("response"):
        response = book_club_repo.create_update_post(update_data)
    else:
        response = book_club_repo.create_update_post_no_text(update_data)

    if response:
        return JSONResponse(
            status_code=200, 
            content={"message":"Post created"})

@router.get("{book_club_id}/feed",
            name="bookclub:get_feed")
async def get_club_feed(
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    filter: Optional[bool] = True,
    book_club_repo: BookClubCRUDRepositoryGraph = 
        Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
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
    """
### Currently Reading Settings Page ########################################################################################

@router.post("/{book_club_id}/currently_reading/start",
            name="bookclub:start_book")
async def start_book_for_club(
    book_club_id:str,
    request:Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = 
        Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
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
        start_currently_reading = BookClubSchemas.StartCurrentlyReading(
            expected_finish_date=datetime.fromisoformat(
                data.get("expected_finish_date")),
            book=data.get("book"),
            user_id=current_user.id,
            id=book_club_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if (not start_currently_reading.book.get("id") or 
            not start_currently_reading.book.get("chapters")):
        raise HTTPException(status_code=400, detail="Missing required value")
    
    result = book_club_repo.create_currently_reading_club(
        start_currently_reading)
    
    if result:
        return JSONResponse(
            status_code=200, 
            content={"message": "Book set as currently reading"})
    else:
        raise HTTPException(
            status_code=404, 
            detail="Error starting book")


@router.post("/{book_club_id}/currently_reading/finish",
             name="bookclub:finish_book")
async def finish_book_for_club(
    book_club_id:str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = 
        Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
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
    result = book_club_repo.update_finished_reading(
        book_club_id,
        current_user.id
    )

    if result:
        return JSONResponse(
            status_code=200, 
            content={"message": "Book set as finished reading"})
    else:
        raise HTTPException(
            status_code=404, 
            detail="Error finishing book")

@router.post("/{book_club_id}/currently_reading/stop",
             name="bookclub:stop_book")
async def stop_book_for_club(
    book_club_id:str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = 
        Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
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
    result = book_club_repo.update_stopped_reading(
        book_club_id,
        current_user.id
    )

    if result:
        return JSONResponse(
            status_code=200, 
            content={"message": "Book set as stopped reading"})
    else:
        raise HTTPException(
            status_code=404, 
            detail="Error finishing book")


@router.get("/{book_club_id}/club_invites",
    name="bookclub:invites_for_club"
)
async def invites_for_bookclub(
    book_club_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    book_club_repo: BookClubCRUDRepositoryGraph = 
        Depends(get_repository(repo_type=BookClubCRUDRepositoryGraph))
) -> None:
    """
    gets all outstanding invites for an admins view of bookclub members setting 
    """
    invites = book_club_repo.get_invites_for_book_club(
        book_club_id=book_club_id,
        user_id=current_user.id
    )

    if invites:
        return JSONResponse(
            status_code=200,
            content={"invites": jsonable_encoder(invites)}
        )
    else:
        print(BookClubSchemas.BaseBookClub.errors)
        raise HTTPException(**BookClubSchemas.BaseBookClub.errors['unauthorized'])