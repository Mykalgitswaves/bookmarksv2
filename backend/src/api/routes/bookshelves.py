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
from typing import Annotated
import asyncio

from src.securities.authorizations.verify import get_current_active_user, get_bookshelf_websocket_user, get_current_user_no_exceptions
from src.api.utils.database import get_repository

from src.models.schemas.users import UserInResponse, User
from src.database.graph.crud.bookshelves import BookshelfCRUDRepositoryGraph
from src.database.graph.crud.books import BookCRUDRepositoryGraph
from src.database.graph.crud.users import UserCRUDRepositoryGraph
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
    BookshelfBookNote
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
            created_by=_bookshelf.created_by
        )
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
            title=_bookshelf.title,
            description=_bookshelf.description,
            books=_bookshelf.books,
            contributors=_bookshelf.contributors,
            follower_count=_bookshelf.follower_count,
            visibility=_bookshelf.visibility,
            members=_bookshelf.members,
            created_by=_bookshelf.created_by,
        )

    return JSONResponse(content={"bookshelf": jsonable_encoder(bookshelf_response)})

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
        return JSONResponse(content={"message": "Contributor added to bookshelf"})
    else:
        raise HTTPException(status_code=400, detail="Failed to add contributor to bookshelf")
    
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
                                  user_id=data['member_id'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if bookshelf.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="User cannot remove themselves as a member to the bookshelf")

    response = bookshelf_repo.delete_bookshelf_member(bookshelf.id, bookshelf.user_id, current_user.id)
    if response:
        if bookshelf_id in bookshelf_ws_manager.cache:
            bookshelf_ws_manager.cache[bookshelf_id].remove_member(bookshelf.user_id)
        return JSONResponse(content={"message": "member added to bookshelf"})
    else:
        raise HTTPException(status_code=400, detail="Failed to add member to bookshelf")
    
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
    
@router.websocket('/ws/{bookshelf_id}') 
async def bookshelf_connection(websocket: WebSocket, 
                               bookshelf_id: str,
                            #    background_tasks: BackgroundTasks,
                               token: str = Query(...),
                               bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph)),
                               user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph)),
                               book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph))):
    print("entered bookshelf_connection")
    try:
        current_user = await get_current_user_no_exceptions(token=token, user_repo=user_repo)
    except:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    # This is responsible for the initial connection to the websocket.
    if not current_user:
        print("user missing")
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
                    # Create task to trun this.
                    await bookshelf_ws_manager.reorder_books_and_send_updated_data(current_user=current_user, bookshelf_id=bookshelf_id, data=data, bookshelf_repo=bookshelf_repo)
            
            elif data['type'] == 'delete':
                try:
                    data = BookshelfBookRemove(
                        book_id=data['target_id'],
                        contributor_id=current_user.id
                    )
                except ValueError as e:
                    await bookshelf_ws_manager.invalid_data_error(bookshelf_id=bookshelf_id)
                    continue

                async with bookshelf_ws_manager.locks[bookshelf_id]:
                    await bookshelf_ws_manager.send_data(data={"state": "locked"}, bookshelf_id=bookshelf_id)

                    await bookshelf_ws_manager.remove_book_and_send_updated_data(current_user=current_user, bookshelf_id=bookshelf_id, data=data, bookshelf_repo=bookshelf_repo)

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
    

# @router.get("/tests/test_background_task",
#             name="bookshelf:test_background_task")
# async def test_background_task(background_tasks: BackgroundTasks):
#     print("Triggering background task")
#     background_tasks.add_task(google_books_background_tasks.simple_task, x=1)
#     return JSONResponse(content={"message": "Task added"})

# TO BE DELETED
# @router.put("/{bookshelf_id}/remove_book",
#             name="bookshelf:remove_item")
# async def remove_item_from_list(request: Request, 
#                                 bookshelf_id: str,
#                                 current_user: Annotated[User, Depends(get_current_active_user)],
#                                 bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
#     data = await request.json()

#     try:
#         data = BookshelfBookRemove(
#             book_id=data['book_id'],
#             contributor_id=current_user.id
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
#     if bookshelf_id in bookshelf_ws_manager.cache:
#         # Pipeline if a book is in the cache.
#         _bookshelf = bookshelf_ws_manager.cache[bookshelf_id]

#         if current_user.id not in _bookshelf.contributors:
#             raise HTTPException(status_code=403, detail="User is not authorized to remove book from this bookshelf")
        
#         if bookshelf_id in bookshelf_ws_manager.locks:
#             # Different logic if the bookshelf has a lock.
#             async with bookshelf_ws_manager.locks[bookshelf_id]:
#                 await bookshelf_ws_manager.send_data(data={"state": "locked"}, bookshelf_id=bookshelf_id)

#                 _bookshelf.remove_book(data.book_id)

#                 books = jsonable_encoder(_bookshelf.get_books())

#                 bookshelf_repo.remove_book(book_to_remove=data.book_id, books=books, bookshelf_id=bookshelf_id)

#                 await bookshelf_ws_manager.send_data(bookshelf_id=bookshelf_id, data={
#                 "state": "unlocked", "data": books })
#         else:
#             # No need to wait for the lock of update the websocket if no lock is present.
#             _bookshelf.remove_book(data.book_id)

#             books = jsonable_encoder(_bookshelf.get_books())

#             bookshelf_repo.remove_book(book_to_remove=data.book_id, books=books, bookshelf_id=bookshelf_id)

#     else:
#         # In this case, we update the order of the book on the db side. 
#         bookshelf_repo.remove_book_advanced(book_to_remove=data.book_id, books=books, bookshelf_id=bookshelf_id)
        
        # TODO: Add get request for all bookshelves for current user.
        #  distinction in return values between bookshelves created by user and bookshelves followed by user.
        # { 
            # 'created-bookshelves' [],
        #   'followed-bookshelves' [],
        # }

        # """
        # Example of a bookshelf object for front end could look like this:
        # followed, contributor, owner.
        # followed shelf objects look like = {
        #     first_four_img_urls of books in bookshelf: [], so we can make css mozaic for picture.
        #     bookshelf_title: 'new',
        #     bookshelf_id: , },
        #     num_books, '',
        #     num_followers: optional
        #     is_contributor: bool
        # }

        # created_shelf_objects = {
        #  ... followed shelf objects have,
        #     visibility
        # }
        # """

# Want to Read bookshelf get for user 
router.get("want_to_read/{user_id}",
            name="bookshelf:want_to_read")
async def get_user_want_to_read(user_id: str,
                                current_user: Annotated[User, Depends(get_current_active_user)],
                                bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    if current_user.id == user_id:
        owner = "current_user"

    bookshelf = bookshelf_repo.get_user_want_to_read(user_id=user_id)

    if bookshelf.visibility == "public" or current_user.id == user_id:   
        return JSONResponse(content={"bookshelves": jsonable_encoder(bookshelf)})
    else:
        raise HTTPException(status_code=403, detail="User is not authorized to view want to read bookshelf of another user")