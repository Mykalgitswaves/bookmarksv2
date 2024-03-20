import fastapi
from fastapi import (
    HTTPException, 
    Depends, 
    BackgroundTasks, 
    Request, 
    WebSocket, 
    WebSocketException,
    WebSocketDisconnect
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated

from src.securities.authorizations.verify import get_current_active_user, get_bookshelf_websocket_user
from src.api.utils.database import get_repository

from src.models.schemas.users import UserInResponse, User
from src.database.graph.crud.bookshelves import BookshelfCRUDRepositoryGraph
from src.database.graph.crud.users import UserCRUDRepositoryGraph
from src.models.schemas.bookshelves import BookshelfCreate, BookshelfResponse, BookshelfId, BookshelfReorder, BookshelfBookRemove, BookshelfBookAdd
from src.api.websockets.bookshelves import bookshelf_ws_manager

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
    if data and data['bookshelf_name'] and data['bookshelf_description'] and data['visibility']:
        name = data['bookshelf_name']
        description = data['bookshelf_description']
        visibility = data['visibility']
        
        try:
            bookshelf = BookshelfCreate(
                created_by=current_user.id,
                title=name,
                description=description,
                visibility=visibility
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        bookshelf_id = bookshelf_repo.create_bookshelf(bookshelf)
        return {"bookshelf_id": bookshelf_id}
    else:
        raise HTTPException(status_code=400, detail="missing name or title")
    
@router.get("/{bookshelf_id}",
            name="bookshelf:get")
async def get_bookshelf(bookshelf_id: str, 
                        current_user:  Annotated[User, Depends(get_current_active_user)],
                        bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph)),
                        user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):
    # For now not using live data pulled from db since we dont have these objects stored there.
    if bookshelf_id in bookshelf_ws_manager.cache:
        _bookshelf = bookshelf_ws_manager.cache[bookshelf_id]
    else:
        _bookshelf = bookshelf_repo.get_bookshelf(bookshelf_id, current_user.id)

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
                bookshelf_ws_manager.cache[bookshelf_id] = _bookshelf

        # Set this in the cache for websocket.

        bookshelf_response = BookshelfResponse(
            title=_bookshelf.title,
            description=_bookshelf.description,
            books=_bookshelf.books,
            contributors=_bookshelf.contributors,
            followers=_bookshelf.followers
        )

    return JSONResponse(content={"bookshelf": jsonable_encoder(bookshelf_response)})

@router.put("/{bookshelf_id}/remove_book",
            name="bookshelf:remove_item")
async def remove_item_from_list(request: Request, 
                                bookshelf_id: str,
                                current_user: Annotated[User, Depends(get_current_active_user)],
                                bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
    data = await request.json()

    try:
        data = BookshelfBookRemove(
            book_id=data['book_id'],
            contributor_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if bookshelf_id in bookshelf_ws_manager.cache:
        # Pipeline if a book is in the cache.
        _bookshelf = bookshelf_ws_manager.cache[bookshelf_id]

        if current_user.id not in _bookshelf.contributors:
            raise HTTPException(status_code=403, detail="User is not authorized to remove book from this bookshelf")
        
        if bookshelf_id in bookshelf_ws_manager.locks:
            # Different logic if the bookshelf has a lock.
            async with bookshelf_ws_manager.locks[bookshelf_id]:
                await bookshelf_ws_manager.send_data(data={"state": "locked"}, bookshelf_id=bookshelf_id)

                _bookshelf.remove_book(data.book_id)

                books = jsonable_encoder(_bookshelf.get_books())

                bookshelf_repo.remove_book(book_to_remove=data.book_id, books=books, bookshelf_id=bookshelf_id)

                await bookshelf_ws_manager.send_data(bookshelf_id=bookshelf_id, data={
                "state": "unlocked", "data": books })
        else:
            # No need to wait for the lock of update the websocket if no lock is present.
            _bookshelf.remove_book(data.book_id)

            books = jsonable_encoder(_bookshelf.get_books())

            bookshelf_repo.remove_book(book_to_remove=data.book_id, books=books, bookshelf_id=bookshelf_id)

    else:
        # In this case, we update the order of the book on the db side. 
        bookshelf_repo.remove_book_advanced(book_to_remove=data.book_id, books=books, bookshelf_id=bookshelf_id)

@router.websocket('/ws/{bookshelf_id}') # This is changing to /api/bookshelf/ws/{bookshelf_id}
async def bookshelf_connection(websocket: WebSocket, 
                               bookshelf_id: str,
                               current_user: Annotated[User, Depends(get_bookshelf_websocket_user)],
                               bookshelf_repo: BookshelfCRUDRepositoryGraph = Depends(get_repository(repo_type=BookshelfCRUDRepositoryGraph))):
        await websocket.accept()
        await bookshelf_ws_manager.connect(bookshelf_id, websocket)
        try:
            while True and bookshelf_id in bookshelf_ws_manager.cache: #CAN THE TRUE BE REMOVED?
                data = await websocket.receive_json()
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
                            target_id=data['target_id'],
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
                        data = BookshelfBookAdd(
                            target_id=data['target_id'],
                            contributor_id=current_user.id
                        )
                    except ValueError as e:
                        await bookshelf_ws_manager.invalid_data_error(bookshelf_id=bookshelf_id)
                        continue

                    async with bookshelf_ws_manager.locks[bookshelf_id]:
                        await bookshelf_ws_manager.send_data(data={"state": "locked"}, bookshelf_id=bookshelf_id)

                        await bookshelf_ws_manager.add_book_and_send_updated_data(current_user=current_user, bookshelf_id=bookshelf_id, data=data, bookshelf_repo=bookshelf_repo)
                


        except WebSocketDisconnect:
            await bookshelf_ws_manager.disconnect(bookshelf_id, websocket)