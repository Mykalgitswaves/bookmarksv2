import fastapi
from fastapi import (
    HTTPException, 
    Depends, 
    BackgroundTasks, 
    Request, 
    WebSocket, 
    WebSocketException,
    WebSocketDisconnect,
    status,
    Query
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated, Optional
import asyncio

from src.securities.authorizations.verify import get_current_active_user, get_bookshelf_websocket_user, get_current_user_no_exceptions
from src.securities.authorizations.jwt import jwt_generator
from src.api.utils.database import get_repository

from src.database.graph.crud.bookshelves import BookshelfCRUDRepositoryGraph
from src.database.graph.crud.books import BookCRUDRepositoryGraph
from src.database.graph.crud.users import UserCRUDRepositoryGraph
from src.database.graph.crud.posts import PostCRUDRepositoryGraph

from src.models.schemas.books import BookId
from src.models.schemas.users import UserInResponse, User, UserId
from src.models.schemas.posts import WantToReadCreate, CurrentlyReadingCreate
from src.models.schemas.bookshelves import (
    BookshelfCreate, 
    BookshelfResponse, 
    BookshelfId, 
    BookshelfReorder, 
    BookshelfBookRemove, 
    BookshelfBookAdd, 
    BookshelfTaskRoute,
    Bookshelf,
    BookshelfBook,
    BookshelfTitle,
    BookshelfDescription,
    BookshelfVisibility,
    BookshelfUser,
    BookshelfPage,
    BookshelfBookNote,
    CurrentlyReadingPageUpdate
)
from src.api.websockets.bookshelves import bookshelf_ws_manager
from src.api.background_tasks.google_books import google_books_background_tasks


router = fastapi.APIRouter(prefix="/bookshelves", tags=["bookshelves"])

@router.post("/create",
            name="bookshelf:create")
async def create_bookshelf(request:Request, 
                          current_user:  Annotated[User, Depends(get_current_active_user)],
                          bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    """
    Create a new bookshelf for the current user.
    """

    data = await request.json()

    try:
        bookshelf = BookshelfCreate(
            created_by=current_user.id,
            title=data['bookshelf_name'],
            description=data['bookshelf_description'],
            visibility=data['visibility']
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    bookshelf_id = bookshelf_repo.create_bookshelf(bookshelf)
    return {"bookshelf_id": bookshelf_id}
    

@router.get("/{bookshelf_id}", 
            name="bookshelf:get")
async def get_bookshelf(bookshelf_id: str, 
                        current_user:  Annotated[User, Depends(get_current_active_user)],
                        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph)),
                        user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):
    # For now not using live data pulled from db since we dont have these objects stored there.
    if bookshelf_id in bookshelf_ws_manager.cache:
        _bookshelf = bookshelf_ws_manager.cache[bookshelf_id]
        _bookshelf = BookshelfPage(
            id=_bookshelf.id,
            img_url=_bookshelf.img_url,
            title=_bookshelf.title,
            description=_bookshelf.description,
            books=_bookshelf.get_books()[0],
            contributors=_bookshelf.contributors,
            follower_count=_bookshelf.follower_count,
            visibility=_bookshelf.visibility,
            members=_bookshelf.members,
            created_by=_bookshelf.created_by,
            created_by_username=_bookshelf.created_by_username
        )
    else:
        if bookshelf_id.startswith("want_to_read"):
            _bookshelf = bookshelf_repo.get_user_want_to_read_by_shelf_id(bookshelf_id=bookshelf_id)
        elif bookshelf_id.startswith("currently_reading"):
            _bookshelf = bookshelf_repo.get_user_currently_reading_by_shelf_id(bookshelf_id=bookshelf_id)
        elif bookshelf_id.startswith("finished_reading"):
            _bookshelf = bookshelf_repo.get_user_finished_reading_by_shelf_id(bookshelf_id=bookshelf_id)
        else:
            _bookshelf = bookshelf_repo.get_bookshelf(bookshelf_id)
    
    if not _bookshelf:
        raise HTTPException(status_code=404, detail="Bookshelf not found")
    else:
        if current_user.id not in _bookshelf.contributors:
            # Check if the user has access to the bookshelf
            if _bookshelf.visibility == "private":
                if current_user.id not in _bookshelf.members:
                    raise HTTPException(status_code=403, detail="User is not authorized to view private bookshelf")

            elif _bookshelf.visibility == "friends":
                friends = user_repo.get_simple_friend_list(_bookshelf.created_by)
                if current_user.id not in friends:
                    raise HTTPException(status_code=403, detail="User is not authorized to view friends only bookshelf")
        else:
            if bookshelf_id not in bookshelf_ws_manager.cache:
                _bookshelf_dll = Bookshelf(
                    title=_bookshelf.title,
                    description=_bookshelf.description,
                    created_by=_bookshelf.created_by,
                    created_by_username=_bookshelf.created_by_username,
                    id=_bookshelf.id,
                    img_url=_bookshelf.img_url,
                    members=_bookshelf.members,
                    follower_count=_bookshelf.follower_count,
                    contributors=_bookshelf.contributors,
                    visibility=_bookshelf.visibility
                )
                for book in _bookshelf.books:
                    _bookshelf_dll.add_book_to_shelf(book, current_user.id)
                bookshelf_ws_manager.cache[bookshelf_id] = _bookshelf_dll

        # Set this in the cache for websocket.
        
        bookshelf_response = BookshelfResponse(
            id=_bookshelf.id,
            title=_bookshelf.title,
            description=_bookshelf.description,
            books=_bookshelf.books,
            contributors=_bookshelf.contributors,
            follower_count=_bookshelf.follower_count,
            visibility=_bookshelf.visibility,
            members=_bookshelf.members,
            created_by=_bookshelf.created_by,
            created_by_username=_bookshelf.created_by_username
        )

    return JSONResponse(content={"bookshelf": jsonable_encoder(bookshelf_response)})

# Endpoint for returning other shelves created by non current user.
# We can probably add some future functionality for recommending bookshelves to users. 
@router.get("/explore/{user_id}", name="bookshelf:explore_bookshelves")
async def get_explore_bookshelves(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph)),
    skip: int=0, 
    limit: int=5,
):
    try:
        user_id_obj = UserId(id=user_id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if current_user.id == user_id_obj.id:
        explore_bookshelves = bookshelf_repo.get_explore_bookshelves_for_user(user_id=user_id_obj.id, skip=skip, limit=limit)
        return JSONResponse(content={"bookshelves": jsonable_encoder(explore_bookshelves)})
    else:
        raise HTTPException(status_code=403, detail="User is not authorized to view a different user's explore bookshelves")


@router.get("/created_bookshelves/{user_id}",
        name="bookshelf:created_bookshelves")
async def get_created_bookshelves(user_id: str, current_user:  Annotated[User, Depends(get_current_active_user)],
    bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph)),
):
    if current_user.id == user_id:
        bookshelves = bookshelf_repo.get_bookshelves_created_by_user(user_id=user_id)    
        return JSONResponse(content={"bookshelves": jsonable_encoder(bookshelves)})
    else:
        raise HTTPException(status_code=403, detail="User is not authorized to view bookshelves created by another user")
    
@router.get("/contributed_bookshelves/{user_id}", 
            name="bookshelf:contributed_bookshelves")
async def get_contributed_bookshelves(user_id: str, 
    current_user:  Annotated[User, Depends(get_current_active_user)],
    bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
):
    if current_user.id == user_id:
        bookshelves = bookshelf_repo.get_bookshelves_contributed_to_by_user(user_id=user_id)    
        return JSONResponse(content={"bookshelves": jsonable_encoder(bookshelves)})
    else:
        raise HTTPException(status_code=403, detail="User is not authorized to view bookshelves contributed to by another user")

@router.get("/member_bookshelves/{user_id}", name="bookshelf:member_bookshelves")
async def get_member_bookshelves(user_id: str,
    current_user:  Annotated[User, Depends(get_current_active_user)],
    bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
):
    if current_user.id == user_id:
        bookshelves = bookshelf_repo.get_bookshelves_member_of_by_user(user_id=user_id)    
        return JSONResponse(content={"bookshelves": jsonable_encoder(bookshelves)})
    else:
        raise HTTPException(status_code=403, detail="User is not authorized to view bookshelves they are a member of")

@router.delete("/{bookshelf_id}/delete", name="bookshelf:delete")
async def delete_bookshelf(bookshelf_id: str, 
    current_user:  Annotated[User, Depends(get_current_active_user)],
    bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
):
    # For now not using live data pulled from db since we dont have these objects stored there.
    try:
        bookshelf_id = BookshelfId(id=bookshelf_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = bookshelf_repo.delete_bookshelf(bookshelf_id.id, current_user.id)
    if response:
        if bookshelf_id.id in bookshelf_ws_manager.cache:
            del bookshelf_ws_manager.cache[bookshelf_id.id]
        return JSONResponse(content={"message": "Bookshelf deleted"})
    else:
        raise HTTPException(status_code=400, detail="Failed to delete bookshelf")
    
@router.put("/{bookshelf_id}/update_title",
            name="bookshelf:update_title")
async def update_bookshelf_title(request: Request,
                                    bookshelf_id: str,
                                    current_user: Annotated[User, Depends(get_current_active_user)],
                                    bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    data = await request.json()

    try:
        bookshelf = BookshelfTitle(id=bookshelf_id,
                                      title=data['title'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = bookshelf_repo.update_bookshelf_title(bookshelf.id, bookshelf.title, current_user.id)
    if response:
        if bookshelf_id in bookshelf_ws_manager.cache:
            bookshelf_ws_manager.cache[bookshelf_id].title = bookshelf.title
        return JSONResponse(content={"message": "Bookshelf title updated"})
    else:
        raise HTTPException(status_code=400, detail="Failed to update bookshelf title")
        
@router.put("/{bookshelf_id}/update_description",
            name="bookshelf:update_description")
async def update_bookshelf_description(request: Request,
                                    bookshelf_id: str,
                                    current_user: Annotated[User, Depends(get_current_active_user)],
                                    bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    data = await request.json()

    try:
        bookshelf = BookshelfDescription(id=bookshelf_id,
                                         description=data['description'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = bookshelf_repo.update_bookshelf_description(bookshelf.id, bookshelf.description, current_user.id)
    if response:
        if bookshelf_id in bookshelf_ws_manager.cache:
            bookshelf_ws_manager.cache[bookshelf_id].description = bookshelf.description
        return JSONResponse(content={"message": "Bookshelf description updated"})
    else:
        raise HTTPException(status_code=400, detail="Failed to update bookshelf description")
    
@router.put("/{bookshelf_id}/update_visibility",
            name="bookshelf:update_visibility")
async def update_bookshelf_visibility(request: Request,
                                    bookshelf_id: str,
                                    current_user: Annotated[User, Depends(get_current_active_user)],
                                    bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    data = await request.json()

    try:
        bookshelf = BookshelfVisibility(id=bookshelf_id,
                                         visibility=data['visibility'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = bookshelf_repo.update_bookshelf_visibility(bookshelf.id, bookshelf.visibility, current_user.id)
    if response:
        if bookshelf_id in bookshelf_ws_manager.cache:
            bookshelf_ws_manager.cache[bookshelf_id].visibility = bookshelf.visibility
        return JSONResponse(content={"message": "Bookshelf visibility updated"})
    else:
        raise HTTPException(status_code=400, detail="Failed to update bookshelf visibility")

@router.put("/{bookshelf_id}/add_contributor",
            name="bookshelf:add_contributor")
async def add_contributor_to_bookshelf(request: Request,
                                        bookshelf_id: str,
                                        current_user:  Annotated[User, Depends(get_current_active_user)],
                                        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    data = await request.json()

    try:
        bookshelf = BookshelfUser(id=bookshelf_id,
                                  user_id=data['contributor_id'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if bookshelf.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="User cannot add themselves as a contributor to the bookshelf")

    response = bookshelf_repo.update_bookshelf_contributors(bookshelf.id, bookshelf.user_id, current_user.id)
    if response:
        if bookshelf_id in bookshelf_ws_manager.cache:
            bookshelf_ws_manager.cache[bookshelf_id].add_contributor(bookshelf.user_id)
        return JSONResponse(content={"message": "Contributor added to bookshelf", "role": "contributor"})
    else:
        raise HTTPException(status_code=400, detail="Failed to add contributor to bookshelf")
    
@router.put("/{bookshelf_id}/remove_contributor",
            name="bookshelf:remove_contributor")
async def remove_contributor_to_bookshelf(request: Request,
                                        bookshelf_id: str,
                                        current_user:  Annotated[User, Depends(get_current_active_user)],
                                        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    data = await request.json()

    try:
        bookshelf = BookshelfUser(id=bookshelf_id,
                                  user_id=data['contributor_id'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if bookshelf.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="User cannot remove themselves as a contributor to the bookshelf")

    response = bookshelf_repo.delete_bookshelf_contributor(bookshelf.id, bookshelf.user_id, current_user.id)
    if response:
        if bookshelf_id in bookshelf_ws_manager.cache:
            bookshelf_ws_manager.cache[bookshelf_id].remove_contributor(bookshelf.user_id)
        return JSONResponse(content={"message": "Contributor removed from bookshelf"})
    else:
        raise HTTPException(status_code=400, detail="Failed to remove contributor from bookshelf")
    
@router.put("/{bookshelf_id}/add_member",
            name="bookshelf:add_member")
async def add_member_to_bookshelf(request: Request,
                                 bookshelf_id: str,
                                 current_user:  Annotated[User, Depends(get_current_active_user)],
                                 bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    data = await request.json()
    
    try:
        bookshelf = BookshelfUser(id=bookshelf_id,
                                  user_id=data['member_id'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if bookshelf.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="User cannot add themselves as a member to the bookshelf")

    response = bookshelf_repo.update_bookshelf_members(bookshelf.id, bookshelf.user_id, current_user.id)
    if response:
        if bookshelf_id in bookshelf_ws_manager.cache:
            bookshelf_ws_manager.cache[bookshelf_id].add_member(bookshelf.user_id)
        return JSONResponse(content={"message": "member added to bookshelf"})
    else:
        raise HTTPException(status_code=400, detail="Failed to add member to bookshelf")
    
@router.put("/{bookshelf_id}/remove_member",
            name="bookshelf:remove_member")
async def remove_member_to_bookshelf(request: Request,
                                        bookshelf_id: str,
                                        current_user:  Annotated[User, Depends(get_current_active_user)],
                                        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    data = await request.json()

    try:
        bookshelf = BookshelfUser(id=bookshelf_id,
                                  user_id=data.get('member_id')
                                )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if bookshelf.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="User cannot remove themselves as a member to the bookshelf")

    response = bookshelf_repo.delete_bookshelf_member(bookshelf.id, bookshelf.user_id, current_user.id)

    if response:
        if bookshelf_id in bookshelf_ws_manager.cache:
            bookshelf_ws_manager.cache[bookshelf_id].remove_member(bookshelf.user_id)
        return JSONResponse(content={"message": "member removed from bookshelf"})
    else:
        raise HTTPException(status_code=400, detail="Failed to remove member from bookshelf")
    
@router.get("/{bookshelf_id}/contributors",
            name="bookshelf:get_contributors")
async def get_contributors(bookshelf_id: str, 
                            current_user:  Annotated[User, Depends(get_current_active_user)],
                            bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    """
    Returns a list of contributors to the bookshelf

    Args:
        bookshelf_id: The id of the bookshelf.

    Returns:
        list(BookshelfContributor): A list of contributors to the bookshelf.
            {
                "user_id": str,
                "username": str,
                "full_name": str,
                "profile_img_url": str
                "relationship_to_current_user": str
                "created_date": datetime
            }
    """
    
    contributors, contributor_ids = bookshelf_repo.get_bookshelf_contributors(bookshelf_id, 
                                                                              current_user.id)

    if current_user.id not in contributor_ids:
        raise HTTPException(status_code=403, detail="User is not authorized to view contributors to this bookshelf")
    else:
        return JSONResponse(content={"contributors": jsonable_encoder(contributors)})
    
@router.get("/{bookshelf_id}/members",
            name="bookshelf:get_members")
async def get_members(bookshelf_id: str,
                        current_user:  Annotated[User, Depends(get_current_active_user)],
                        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    """
    Returns a list of members to the bookshelf
    """

    members, member_ids = bookshelf_repo.get_bookshelf_members(bookshelf_id, 
                                                    current_user.id)
    
    if current_user.id not in bookshelf_repo.get_bookshelf_contributors(bookshelf_id, current_user.id)[1] and current_user.id not in member_ids:
        raise HTTPException(status_code=403, detail="User is not authorized to view members of this bookshelf")
    else:
        return JSONResponse(content={"members": jsonable_encoder(members)})

#Router for getting all followers of a bookshelf
@router.get("/{bookshelf_id}/followers",
            name="bookshelf:get_followers")
async def get_followers(bookshelf_id: str,
                        current_user: Annotated[User, Depends(get_current_active_user)],
                        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    
    followers = bookshelf_repo.get_bookshelf_followers(bookshelf_id, current_user.id)
    return JSONResponse(content={"followers": jsonable_encoder(followers)})  

@router.put("/{bookshelf_id}/update_book_note",
            name="bookshelf:update_book_note")
async def update_book_note(request: Request,
                            bookshelf_id: str,
                            current_user: Annotated[User, Depends(get_current_active_user)],
                            bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    data = await request.json()
    print(data)
    # Build the request data
    try:
        bookshelf = BookshelfBookNote(
            book_id=data['book_id'],
            note_for_shelf=data['note_for_shelf'],
            id=bookshelf_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Check if the bookshelf is cached
    if bookshelf_id in bookshelf_ws_manager.cache:
        #Check user permissions
        if current_user.id not in bookshelf_ws_manager.cache[bookshelf_id].contributors:
            raise HTTPException(status_code=403, detail="User is not authorized to update book note for this bookshelf")
        
        # Update the book note in the cache
        status = bookshelf_ws_manager.cache[bookshelf_id].update_book_note(bookshelf.book_id, bookshelf.note_for_shelf)
        # Check that the book was found in the bookshelf
        if status:
            # Update the book note in the database
            prefixes = ["want_to_read", "currently_reading", "finished_reading"]
            # if any of the prefixes are in the bookshelf_id, then we are dealing with a user bookshelf
            if any(prefix in bookshelf_id for prefix in prefixes):
                repo_status = bookshelf_repo.update_book_note_for_shelf_reading_flow(bookshelf_id, 
                                                      bookshelf.book_id, 
                                                      bookshelf.note_for_shelf,
                                                      current_user.id)
            else:
                repo_status = bookshelf_repo.update_book_note_for_shelf(bookshelf_id, 
                                                        bookshelf.book_id, 
                                                        bookshelf.note_for_shelf,
                                                        current_user.id)
            
            # Check that the book note was updated in the database
            if repo_status:
                # Grab the books from the cache
                books, book_ids = bookshelf_ws_manager.cache[bookshelf_id].get_books()

                books = jsonable_encoder(books)

                # Send the updated data to the websocket
                await bookshelf_ws_manager.send_data(bookshelf_id=bookshelf_id, data={
                "state": "unlocked", "data": books })

                # Return a success message
                return JSONResponse(content={"message": "Book note updated"})
            else:
                raise HTTPException(status_code=400, detail="Book updated in cache but failed to update in db")
        else:
            raise HTTPException(status_code=404, detail="Book not found in bookshelf")
    else:
        # Update the book note in the database
        repo_status = bookshelf_repo.update_book_note_for_shelf(bookshelf_id, 
                                                                bookshelf.book_id, 
                                                                bookshelf.note_for_shelf,
                                                                current_user.id)
        if repo_status:
            # Return a success message
            return JSONResponse(content={"message": "Book note updated"})
        else:
            raise HTTPException(status_code=400, detail="Failed to update book note")      

#Router for following a bookshelf
@router.put("/{bookshelf_id}/follow",
            name="bookshelf:follow")
async def follow_bookshelf(bookshelf_id: str,
                            current_user: Annotated[User, Depends(get_current_active_user)],
                            bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    
    response = bookshelf_repo.create_follow_bookshelf_rel(bookshelf_id, current_user.id)
    if response:
        return JSONResponse(content={"message": "Bookshelf followed"})
    else:
        raise HTTPException(status_code=400, detail="Bookshelf could not be found or is not public")

#Router for unfollowing a bookshelf
@router.put("/{bookshelf_id}/unfollow",
            name="bookshelf:unfollow")
async def unfollow_bookshelf(bookshelf_id: str,
                            current_user: Annotated[User, Depends(get_current_active_user)],
                            bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    
    response = bookshelf_repo.delete_follow_bookshelf_rel(bookshelf_id, current_user.id)
    if response:
        return JSONResponse(content={"message": "Bookshelf unfollowed"})
    else:
        raise HTTPException(status_code=400, detail="Bookshelf could not be found or is not public")
    
# Want to Read bookshelf get for user 
@router.get("/want_to_read/{user_id}",
            name="bookshelf:want_to_read")
async def get_user_want_to_read(user_id: str,
                                current_user: Annotated[User, Depends(get_current_active_user)],
                                bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    
    try:
        user_id_obj = UserId(id=user_id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    bookshelf = bookshelf_repo.get_user_want_to_read(user_id=user_id_obj.id)

    if not bookshelf:
        raise HTTPException(status_code=404, detail="Want to read bookshelf not found")
    
    if bookshelf.id not in bookshelf_ws_manager.cache:
        bookshelf_dll = Bookshelf(
            title=bookshelf.title,
            description=bookshelf.description,
            created_by=bookshelf.created_by,
            created_by_username=bookshelf.created_by_username,
            current_user_is_admin=current_user.id == bookshelf.created_by,
            id=bookshelf.id,
            img_url=bookshelf.img_url,
            members=bookshelf.members,
            follower_count=bookshelf.follower_count,
            contributors=bookshelf.contributors,
            visibility=bookshelf.visibility
        )
        for book in bookshelf.books:
            bookshelf_dll.add_book_to_shelf(book, current_user.id)
        bookshelf_ws_manager.cache[bookshelf.id] = bookshelf_dll
        
    if bookshelf.visibility == "public" or current_user.id == user_id:
        bookshelf_response = BookshelfResponse(
            id=bookshelf.id,
            title=bookshelf.title,
            description=bookshelf.description,
            books=bookshelf.books,
            contributors=bookshelf.contributors,
            follower_count=bookshelf.follower_count,
            visibility=bookshelf.visibility,
            members=bookshelf.members,
            created_by=bookshelf.created_by,
            created_by_username=bookshelf.created_by_username,
            current_user_is_admin=current_user.id == bookshelf.created_by
        )

        return JSONResponse(content={"bookshelf": jsonable_encoder(bookshelf_response)})
    else:
        raise HTTPException(status_code=403, detail="User is not authorized to view want to read bookshelf of another user")
    
# Currently reading bookshelf get for user 
@router.get("/currently_reading/{user_id}",
            name="bookshelf:currently_reading")
async def get_user_currently_reading(
        user_id: str,
        current_user: Annotated[User, Depends(get_current_active_user)],
        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
        ):
    
    try:
        user_id_obj = UserId(id=user_id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    bookshelf = bookshelf_repo.get_user_currently_reading(user_id=user_id_obj.id)

    if not bookshelf:
        raise HTTPException(status_code=404, detail="Currently reading bookshelf not found")

    if bookshelf.id not in bookshelf_ws_manager.cache:
        bookshelf_dll = Bookshelf(
            title=bookshelf.title,
            description=bookshelf.description,
            created_by=bookshelf.created_by,
            created_by_username=bookshelf.created_by_username,
            id=bookshelf.id,
            img_url=bookshelf.img_url,
            members=bookshelf.members,
            follower_count=bookshelf.follower_count,
            contributors=bookshelf.contributors,
            visibility=bookshelf.visibility
        )
        for book in bookshelf.books:
            bookshelf_dll.add_book_to_shelf(book, current_user.id)
        bookshelf_ws_manager.cache[bookshelf.id] = bookshelf_dll
        
    if bookshelf.visibility == "public" or current_user.id == user_id:
        bookshelf_response = BookshelfResponse(
            id=bookshelf.id,
            title=bookshelf.title,
            description=bookshelf.description,
            books=bookshelf.books,
            contributors=bookshelf.contributors,
            follower_count=bookshelf.follower_count,
            visibility=bookshelf.visibility,
            members=bookshelf.members,
            created_by=bookshelf.created_by,
            created_by_username=bookshelf.created_by_username
        )
        return JSONResponse(content={"bookshelf": jsonable_encoder(bookshelf_response)})
    else:
        raise HTTPException(status_code=403, detail="User is not authorized to view want to read bookshelf of another user")


@router.get("/currently_reading/${user_id}/currently_reading_book/${book_id}/updates_for_current_page",  name="bookshelf:updates_for_currently_reading_page")
async def updates_for_currently_reading_book_by_page_range(
        user_id: str,
        book_id: str,
        starting_page_for_range: int | None,
        size_of_range: int | None,
        updates_per_page: int | None,
        current_user: Annotated[User, Depends(get_current_active_user)],
        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
):
    """
    Returns currently reading updates based on a page passed in as a query param.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=500, detail="Unauthorized")
    
    try:
        user_id_obj = UserId(id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Default values for range size and updates per page.
    size_of_range = size_of_range if not None else 20
    updates_per_page = updates_per_page if not None else 10

    updates = bookshelf_repo.get_update_previews_for_currently_reading_shelf_by_range(
        user_id=user_id_obj.id,
        book_id=book_id,
        starting_page_for_range=starting_page_for_range,
        end_of_range=int(size_of_range + starting_page_for_range),
        updates_per_page=5 
    )

    if not updates:
        return HTTPException(status_code=404, detail="Update not found")
    

# Finished Reading bookshelf get for user 
@router.get("/finished_reading/{user_id}",
            name="bookshelf:want_to_read")
async def get_user_finished_reading(
        user_id: str,
        current_user: Annotated[User, Depends(get_current_active_user)],
        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
        ):
    try:
        user_id_obj = UserId(id=user_id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    bookshelf = bookshelf_repo.get_user_finished_reading(user_id=user_id_obj.id)

    if not bookshelf:
        raise HTTPException(status_code=404, detail="Finished reading bookshelf not found")

    if bookshelf.id not in bookshelf_ws_manager.cache:
        bookshelf_dll = Bookshelf(
            title=bookshelf.title,
            description=bookshelf.description,
            created_by=bookshelf.created_by,
            created_by_username=bookshelf.created_by_username,
            id=bookshelf.id,
            img_url=bookshelf.img_url,
            members=bookshelf.members,
            follower_count=bookshelf.follower_count,
            contributors=bookshelf.contributors,
            visibility=bookshelf.visibility
        )
        for book in bookshelf.books:
            bookshelf_dll.add_book_to_shelf(book, current_user.id)
        bookshelf_ws_manager.cache[bookshelf.id] = bookshelf_dll
        
    if bookshelf.visibility == "public" or current_user.id == user_id:
        bookshelf_response = BookshelfResponse(
            id=bookshelf.id,
            title=bookshelf.title,
            description=bookshelf.description,
            books=bookshelf.books,
            contributors=bookshelf.contributors,
            follower_count=bookshelf.follower_count,
            visibility=bookshelf.visibility,
            members=bookshelf.members,
            created_by=bookshelf.created_by,
            created_by_username=bookshelf.created_by_username
        )
        return JSONResponse(content={"bookshelf": jsonable_encoder(bookshelf_response)})
    else:
        raise HTTPException(status_code=403, detail="User is not authorized to view want to read bookshelf of another user")
    
@router.get("/want_to_read/{user_id}/preview",
            name="bookshelf:want_to_read_preview")
async def get_user_want_to_read_preview(
        user_id: str,
        current_user: Annotated[User, Depends(get_current_active_user)],
        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
        ):
    
    try:
        user_id_obj = UserId(id=user_id)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if current_user.id != user_id_obj.id:
        raise HTTPException(status_code=403, detail="User is not authorized to preview want to read bookshelf of another user")
    
    bookshelf = bookshelf_repo.get_user_want_to_read_preview(user_id=user_id_obj.id)

    if bookshelf:
        return JSONResponse(content={"bookshelf": jsonable_encoder(bookshelf)})
    else:
        raise HTTPException(status_code=404, detail="Want to read bookshelf not found")


@router.get("/minimal_shelves_for_user/{user_id}",
            name="bookshelves:minimal_shelves_for_user")
async def get_users_minimal_shelves(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
):
    try:
        user_id_obj = UserId(id=user_id)
        if current_user.id == user_id_obj.id:
            bookshelves = bookshelf_repo.get_minimal_shelves_for_user(user_id=user_id_obj.id)
            if bookshelves:
                return JSONResponse(content={"bookshelves": jsonable_encoder(bookshelves)})

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/currently_reading/{user_id}/preview",
            name="bookshelf:currently_reading_preview")
async def get_user_currently_reading_preview(
        user_id: str,
        current_user: Annotated[User, Depends(get_current_active_user)],
        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
        ):
    
    try:
        user_id_obj = UserId(id=user_id)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if current_user.id != user_id_obj.id:
        raise HTTPException(status_code=403, detail="User is not authorized to preview currently reading bookshelf of another user")
    
    bookshelf = bookshelf_repo.get_user_currently_reading_preview(user_id=user_id_obj.id)

    if bookshelf:
        return JSONResponse(content={"bookshelf": jsonable_encoder(bookshelf)})
    else:
        raise HTTPException(status_code=404, detail="Currently reading bookshelf not found")


@router.get("/currently_reading/{user_id}/front_page",
            name="bookshelf:currently_reading_front_page")
async def get_user_currently_reading_front_page(
        user_id: str,
        current_user: Annotated[User, Depends(get_current_active_user)],
        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
        ):
    
    try:
        user_id_obj = UserId(id=user_id)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if current_user.id != user_id_obj.id:
        raise HTTPException(status_code=403, detail="User is not authorized to preview currently reading bookshelf of another user")
    
    bookshelf = bookshelf_repo.get_user_currently_reading_front_page(user_id=user_id_obj.id)

    if bookshelf:
        return JSONResponse(content={"bookshelf": jsonable_encoder(bookshelf)})
    else:
        raise HTTPException(status_code=404, detail="Currently reading bookshelf not found")
    
@router.put("/currently_reading/{user_id}/update_current_page",
            name="bookshelf:update_current_page")
async def update_book_current_page(
        request: Request,
        user_id: str,
        current_user: Annotated[User, Depends(get_current_active_user)],
        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
        ):
    
    data = await request.json()
    
    try:
        currently_reading_page_update = CurrentlyReadingPageUpdate(
            user_id=user_id,
            book_id=data['book_id'],
            new_current_page=data['new_current_page'])
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if current_user.id != currently_reading_page_update.user_id:
        raise HTTPException(status_code=403, detail="User is not authorized to perform this action")
    
    result = bookshelf_repo.update_currently_reading_page(
        user_id=currently_reading_page_update.user_id,
        book_id=currently_reading_page_update.book_id,
        new_current_page=currently_reading_page_update.new_current_page)

    if result:
        # Return 200
        return JSONResponse(content={"message": "Current page updated"})
    else:
        raise HTTPException(status_code=404, detail="Error running query to update current page for book in currently reading bookshelf")

    
@router.get("/finished_reading/{user_id}/preview",
            name="bookshelf:finished_reading_preview")
async def get_user_finished_reading_preview(
        user_id: str,
        current_user: Annotated[User, Depends(get_current_active_user)],
        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
        ):
    
    try:
        user_id_obj = UserId(id=user_id)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if current_user.id != user_id_obj.id:
        raise HTTPException(status_code=403, detail="User is not authorized to preview finished reading bookshelf of another user")
    
    bookshelf = bookshelf_repo.get_user_finished_reading_preview(user_id=user_id_obj.id)

    if bookshelf:
        return JSONResponse(content={"bookshelf": jsonable_encoder(bookshelf)})
    else:
        raise HTTPException(status_code=404, detail="Finished reading bookshelf not found")
    
# Quick add book to bookshelf
@router.put("/quick_add/{bookshelf_id}",
            name="bookshelf:quick_add")
async def quick_add_book_to_bookshelf(
    request: Request,
    bookshelf_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    background_tasks:BackgroundTasks,
    move_from: Optional[str] = None,
    bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph)),
    book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph)),
    post_repo: PostCRUDRepositoryGraph = Depends(get_repository(repo_type=PostCRUDRepositoryGraph))
):
    """
    Adds a book to any bookshelf without creating a connection to the websocket
    ARGS:
        request: request object that contains the following data:
            book: dict containing the following keys:
                title: str
                author_names: list[str]
                small_img_url: str
                id: str
            note_for_shelf: str (optional
        bookshelf_id: (str) the id of the bookshelf, or the keyword "want_to_read", "currently_reading", "finished_reading")
        current_user: (User) the current user
        move_from: (str) the previous shelf id if you want to remove the book from that shelf, or the keyword "want_to_read", "currently_reading", "finished_reading" 
    
    If a book is added to one of WantToRead/CurrentlyReading, a simple post will be made
    """
    data = await request.json()
    try:
        book_data = BookshelfBookAdd(
            book=BookshelfBook(
                title=data['book']['title'],
                authors=data['book']['author_names'],
                small_img_url=data['book']['small_img_url'],
                id=data['book']['id'],
                # add a get for note_for_shelf incase null
                note_for_shelf=data['book'].get('note_for_shelf', None)
            ),
            contributor_id=current_user.id,
            move_from=move_from
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    prefixes = ["want_to_read", "currently_reading", "finished_reading"]
    
    # Check google book id to see if its in the database
    book_exists = True
    if book_data.book.id[0] == "g":
        book_exists = False
        canonical_book = book_repo.get_canonical_book_by_google_id_extended(book_data.book.id) 
        if canonical_book:
            book_exists = True
            book_data.book = canonical_book

    # if "note_for_shelf" in data['book']:
    #     book_data.book.note_for_shelf = data['book']["note_for_shelf"]

    # Delete the book from the previous shelf if it exists
    if book_data.move_from:
        # Check if the book exists in the database
        if not book_exists:
            raise HTTPException(status_code=400, detail="Book does not exist in database and therefore cannot be moved to a shelf")

        # Check the reading flow shelves by explicit name
        if book_data.move_from == "want_to_read":
            # We need to run the query first to get the book id
            want_to_read_bookshelf_id = bookshelf_repo.delete_book_from_want_to_read(book_data.book.id, current_user.id)

            # Check if the query executed successfully
            if not want_to_read_bookshelf_id:
                raise HTTPException(status_code=400, detail="Failed to remove book from previous shelf")
            
            # Check if the bookshelf is in the cache
            if want_to_read_bookshelf_id in bookshelf_ws_manager.cache:
                bookshelf_ws_manager.remove_book_only_from_cache(want_to_read_bookshelf_id, book_data)
        
        elif book_data.move_from == "currently_reading":
            currently_reading_bookshelf_id = bookshelf_repo.delete_book_from_currently_reading(book_data.book.id, current_user.id)

            # Check if the query executed successfully
            if not currently_reading_bookshelf_id:
                raise HTTPException(status_code=400, detail="Failed to remove book from previous shelf")
            
            # Check if the bookshelf is in the cache
            if currently_reading_bookshelf_id and currently_reading_bookshelf_id in bookshelf_ws_manager.cache:
                bookshelf_ws_manager.remove_book_only_from_cache(currently_reading_bookshelf_id, book_data)

        elif book_data.move_from == "finished_reading":
            finished_reading_bookshelf_id = bookshelf_repo.delete_book_from_finished_reading(book_data.book.id, current_user.id)

            # Check if the query executed successfully
            if not finished_reading_bookshelf_id:
                raise HTTPException(status_code=400, detail="Failed to remove book from previous shelf")
            
            # Check if the bookshelf is in the cache
            if finished_reading_bookshelf_id and finished_reading_bookshelf_id in bookshelf_ws_manager.cache:
                bookshelf_ws_manager.remove_book_only_from_cache(finished_reading_bookshelf_id, book_data)

        # Now handle the other cases where the shelf is not a reading flow shelf
        else:
            if bookshelf_id.id in bookshelf_ws_manager.cache:
                response = await bookshelf_ws_manager.remove_book_and_send_updated_data_quick(
                    current_user=current_user, 
                    bookshelf_id=bookshelf_id, 
                    data=data, 
                    bookshelf_repo=bookshelf_repo)
                if not response:
                    raise HTTPException(status_code=400, detail="Failed to remove book from previous shelf")
                    
            else:
                # If the bookshelf is not in the cache, we need to run the query and validate the user permissions
                # Check the bookshelf id for keywords
                if any(prefix in book_data.move_from for prefix in prefixes):
                    response = bookshelf_repo.delete_book_from_reading_flow_bookshelf_with_validate(book_data.book.id, book_data.move_from, current_user.id)
                else:
                    response = bookshelf_repo.delete_book_from_bookshelf_with_validate(book_data.book.id, bookshelf_id.id, current_user.id)
                if not response:
                    raise HTTPException(status_code=400, detail="Failed to remove book from previous shelf")
    
    # Add query for reading flow shelves
    if bookshelf_id in prefixes:
        # Check if the book exists in the database
        if book_exists:
            response = bookshelf_repo.create_book_in_reading_flow_bookshelf_rel(book_data.book, bookshelf_id, current_user.id)
        else:
            response = bookshelf_repo.create_book_in_reading_flow_bookshelf_rel_and_book(book_data.book, bookshelf_id, current_user.id)

            # Run background task to update the google book
            if response:
                background_tasks.add_task(
                    google_books_background_tasks.update_book_google_id,
                    book_data.book.id,
                    book_repo)
        if response:
            if bookshelf_id == 'want_to_read':
                background_tasks.add_task(
                        post_repo.create_want_to_read_post,
                        WantToReadCreate(
                            book_id=book_data.book.id,
                            user_id=current_user.id,
                            headline=book_data.book.note_for_shelf
                        )
                    )
            
            elif bookshelf_id == 'currently_reading':
                background_tasks.add_task(
                        post_repo.create_currently_reading_post,
                        CurrentlyReadingCreate(
                            book_id=book_data.book.id,
                            user_id=current_user.id,
                            headline=book_data.book.note_for_shelf
                        )
                    )
                
            return JSONResponse(content={
                    "message": "Book added successfully", 
                    "book": jsonable_encoder(book_data.book)
                })
        else:
            raise HTTPException(status_code=400, detail="Failed to add book to bookshelf, it may already exist in the desitnation shelf")
    
    else: 
        # Check the cache for the bookshelf
        if bookshelf_id in bookshelf_ws_manager.cache:
            google_id_to_add = await bookshelf_ws_manager.add_book_and_send_updated_data_quick(
                current_user=current_user, 
                bookshelf_id=bookshelf_id, 
                data=book_data, 
                bookshelf_repo=bookshelf_repo,
                book_repo=book_repo,
                book_exists=book_exists)
            
            # Check if the book exists in the database
            if google_id_to_add:
                background_tasks.add_task(
                    google_books_background_tasks.update_book_google_id,
                    google_id_to_add,
                    book_repo)
                
            return JSONResponse(content={"message": "Book added successfully"})
        else:
            # If the bookshelf is not in the cache, we need to run the query and validate the user permissions
            # Check the bookshelf id for keywords
            if any(prefix in bookshelf_id for prefix in prefixes):
                if book_exists:
                    response = bookshelf_repo.create_book_in_reading_flow_bookshelf_rel_with_shelf_id(book_data.book, bookshelf_id, current_user.id)
                else:
                    response = bookshelf_repo.create_book_in_reading_flow_bookshelf_rel_with_shelf_id_and_book(book_data.book, bookshelf_id, current_user.id)

            else:
                # These are the normal bookshelf cases
                if book_exists:
                    # TODO Leave this until we fix problems with queries.
                    print('normal bookshelf cases: book exists')
                    response = bookshelf_repo.create_book_in_bookshelf_rel(book_data.book, bookshelf_id, current_user.id)
                else:
                    print('normal bookshelf cases: book does not exist')
                    response = bookshelf_repo.create_book_in_bookshelf_rel_and_book(book_data.book, bookshelf_id, current_user.id)
                    

            if response:
                if not book_exists:
                    background_tasks.add_task(
                            google_books_background_tasks.update_book_google_id,
                            book_data.book.id,
                            book_repo)
                    
                if bookshelf_id.startswith("want_to_read"):
                    background_tasks.add_task(
                        post_repo.create_want_to_read_post,
                        WantToReadCreate(
                            book_id=book_data.book.id,
                            user_id=current_user.id,
                            headline=book_data.book.note_for_shelf
                        )
                    )

                elif bookshelf_id.startswith("currently_reading"):
                    background_tasks.add_task(
                        post_repo.create_currently_reading_post,
                        CurrentlyReadingCreate(
                            book_id=book_data.book.id,
                            user_id=current_user.id,
                            headline=book_data.book.note_for_shelf
                        )
                    )
                    

                return JSONResponse(content={"message": "Book added successfully"})
            else:
                raise HTTPException(status_code=400, detail="Failed to add book to bookshelf")
    
@router.get("/{bookshelf_id}/get_token",
            name="bookshelf:get_token")
async def get_bookshelf_websocket_token(
    bookshelf_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))
    ):
    """
    Get the websocket token for a bookshelf
    """
    if bookshelf_id not in bookshelf_ws_manager.cache:
        if bookshelf_id.startswith("want_to_read"):
            _bookshelf = bookshelf_repo.get_user_want_to_read_by_shelf_id(bookshelf_id=bookshelf_id)
        elif bookshelf_id.startswith("currently_reading"):
            _bookshelf = bookshelf_repo.get_user_currently_reading_by_shelf_id(bookshelf_id=bookshelf_id)
        elif bookshelf_id.startswith("finished_reading"):
            _bookshelf = bookshelf_repo.get_user_finished_reading_by_shelf_id(bookshelf_id=bookshelf_id)
        else:
            _bookshelf = bookshelf_repo.get_bookshelf(bookshelf_id)
    
        if not _bookshelf:
            raise HTTPException(status_code=404, detail="Bookshelf not found")
        else:
            if current_user.id not in _bookshelf.contributors:
                raise HTTPException(status_code=403, detail="User is not authorized to edit this bookshelf")

            else:
                if bookshelf_id not in bookshelf_ws_manager.cache:
                    _bookshelf_dll = Bookshelf(
                        title=_bookshelf.title,
                        description=_bookshelf.description,
                        created_by=_bookshelf.created_by,
                        created_by_username=_bookshelf.created_by_username,
                        id=_bookshelf.id,
                        img_url=_bookshelf.img_url,
                        members=_bookshelf.members,
                        follower_count=_bookshelf.follower_count,
                        contributors=_bookshelf.contributors,
                        visibility=_bookshelf.visibility
                    )
                    for book in _bookshelf.books:
                        _bookshelf_dll.add_book_to_shelf(book, current_user.id)
                    bookshelf_ws_manager.cache[bookshelf_id] = _bookshelf_dll
    
    if current_user.id not in bookshelf_ws_manager.cache[bookshelf_id].contributors:
        print("user not in contributors")
        raise HTTPException(status_code=403, detail="User is not authorized to connect to this bookshelf")
    
    print('New User Established Connection to Bookshelf WS. Generating unique token...')
    token = jwt_generator.generate_bookshelf_websocket_token(user_id=current_user.id, bookshelf_id=bookshelf_id)

    # Return token test
    return JSONResponse(content={"token": token})
    

@router.websocket('/ws/{bookshelf_id}') 
async def bookshelf_connection(websocket: WebSocket, 
                               bookshelf_id: str,
                               token: str = Query(...),
                               bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph)),
                               user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph)),
                               book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph))):
    print("entered bookshelf_connection")
    
    try:
        current_user = await get_bookshelf_websocket_user(token=token)
    except:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    if current_user.bookshelf_id != bookshelf_id:
        print("bookshelf_id mismatch")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if bookshelf_id not in bookshelf_ws_manager.cache:
        print("bookshelf missing")
    # THIS NEEDS TO REDIRECT TO THE /api/bookshelves/{bookshelf_id} endpoint
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    if current_user.id not in bookshelf_ws_manager.cache[bookshelf_id].contributors:
        print("user not in contributors")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await websocket.accept()
    await bookshelf_ws_manager.connect(bookshelf_id, current_user.id, websocket)
    
    try:
        while True and bookshelf_id in bookshelf_ws_manager.cache: #CAN THE TRUE BE REMOVED?
            data = await websocket.receive_json()
            background_tasks = BackgroundTasks()
            print(data)
            try:
                task = BookshelfTaskRoute(
                    type = data['type'],
                    token=data['token']
                )
            except ValueError as e:
                await bookshelf_ws_manager.invalid_data_error(bookshelf_id=bookshelf_id)
                continue
            
            try:
                current_user = await get_bookshelf_websocket_user(token=task.token)
            except:
                await bookshelf_ws_manager.disconnect(bookshelf_id, websocket)
                return
            # We will distinguish between the types of data that can be sent.
            # {"type:"}'reorder' 'add' 'delete'
            if data['type'] == 'reorder':
                try:
                    data = BookshelfReorder(
                        target_id=data['target_id'],
                        previous_book_id=data['previous_book_id'],
                        next_book_id=data['next_book_id'],
                        contributor_id=current_user.id
                    )
                except ValueError as e:
                    await bookshelf_ws_manager.invalid_data_error(bookshelf_id=bookshelf_id)
                    continue
                async with bookshelf_ws_manager.locks[bookshelf_id]:
                    # Lock out the bookshelf on the client while reorder is happening.
                    await bookshelf_ws_manager.send_data(data={"state": "locked"}, bookshelf_id=bookshelf_id)
                    # Create task to run this.
                    await bookshelf_ws_manager.reorder_books_and_send_updated_data(current_user=current_user, bookshelf_id=bookshelf_id, data=data, bookshelf_repo=bookshelf_repo)
            
            elif data['type'] == 'delete':
                try:
                    data = BookshelfBookRemove(
                        book=BookId(
                            id=data['target_id']
                        ),
                        contributor_id=current_user.id
                    )
                except ValueError as e:
                    await bookshelf_ws_manager.invalid_data_error(bookshelf_id=bookshelf_id)
                    continue

                async with bookshelf_ws_manager.locks[bookshelf_id]:
                    await bookshelf_ws_manager.send_data(data={"state": "locked"}, bookshelf_id=bookshelf_id)

                    await bookshelf_ws_manager.remove_book_and_send_updated_data(
                        current_user=current_user, 
                        bookshelf_id=bookshelf_id, 
                        data=data, 
                        bookshelf_repo=bookshelf_repo)

            elif data['type'] == 'add':
                try:
                    book_data = BookshelfBookAdd(
                        book=BookshelfBook(
                            title=data['book']['title'],
                            authors=data['book']['author_names'],
                            small_img_url=data['book']['small_img_url'],
                            id=data['book']['id']
                        ),
                        contributor_id=current_user.id
                    )
                    
                except ValueError as e:
                    await bookshelf_ws_manager.invalid_data_error(bookshelf_id=bookshelf_id)
                    continue
                
                book_exists = True
                if book_data.book.id[0] == "g":
                    book_exists = False
                    canonical_book = book_repo.get_canonical_book_by_google_id_extended(book_data.book.id) 
                    if canonical_book:
                        book_exists = True
                        book_data.book = canonical_book

                if "note_for_shelf" in data['book']:
                        book_data.book.note_for_shelf = data['book']["note_for_shelf"]

                async with bookshelf_ws_manager.locks[bookshelf_id]:
                    await bookshelf_ws_manager.send_data(data={"state": "locked"}, bookshelf_id=bookshelf_id)

                    google_id_to_add = await bookshelf_ws_manager.add_book_and_send_updated_data(current_user=current_user, 
                                                                              bookshelf_id=bookshelf_id, 
                                                                              data=book_data, 
                                                                              bookshelf_repo=bookshelf_repo,
                                                                              book_repo=book_repo,
                                                                              book_exists=book_exists)
                    if google_id_to_add:
                        print("Triggering background task to update book google id")
                        task = asyncio.create_task(google_books_background_tasks.update_book_google_id(google_id=google_id_to_add,
                                                                                                       book_repo=book_repo))
                        background_tasks.add_task(task)
            else:
                await bookshelf_ws_manager.invalid_data_error(bookshelf_id=bookshelf_id)
                continue

    except WebSocketDisconnect:
        await bookshelf_ws_manager.disconnect_without_close(bookshelf_id, websocket)

