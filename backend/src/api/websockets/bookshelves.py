import asyncio
from fastapi import WebSocket, HTTPException
from fastapi.encoders import jsonable_encoder
from src.database.graph.crud.bookshelves import BookshelfCRUDRepositoryGraph
from src.securities.authorizations.jwt import jwt_generator

class BookshelfWSManager:
    def __init__(self):
        self.ac = {}
        self.cache = {}
        self.locks = {}
        self.errors = {
            'INVALID_DATA_ERROR': {'error': 'Cannot reorder. Current, next or previous data was not provided.'},
            'FAILED_TO_REORDER': {'error': 'Reorder failed, change was not processed.'},
        }

        
    async def connect(self, bookshelf_id: str, user_id: str, ws: WebSocket):
        if bookshelf_id not in self.ac:
            self.ac[bookshelf_id] = set()

        self.ac[bookshelf_id].add(ws)
        
        if bookshelf_id not in self.locks:
            self.locks[bookshelf_id] = asyncio.Lock()

        books, book_ids = jsonable_encoder(self.cache[bookshelf_id].get_books())

        print('New User Established Connection to Bookshelf WS. Generating unique token...')
        token = jwt_generator.generate_bookshelf_websocket_token(user_id=user_id, bookshelf_id=bookshelf_id)

        # SHOULD THIS BE A SEND JSON INSTEAD? NO NEED TO SEND A MESSAGE TO THE ENTIRE GROUP
        # await self.send_data(data={
        #     "state": "unlocked", "data": books }, bookshelf_id=bookshelf_id)
        await ws.send_json(data={
            "state": "unlocked", "data": books, "token":token})
        

    async def disconnect(self, bookshelf_id: str, ws: WebSocket):
        self.ac[bookshelf_id].remove(ws)
        if not self.ac[bookshelf_id]:
            del self.ac[bookshelf_id]
            del self.locks[bookshelf_id]
            del self.cache[bookshelf_id]
        await ws.close()

    async def disconnect_without_close(self, bookshelf_id: str, ws: WebSocket):
        self.ac[bookshelf_id].remove(ws)
        if not self.ac[bookshelf_id]:
            del self.ac[bookshelf_id]
            del self.locks[bookshelf_id]
            del self.cache[bookshelf_id]
            
        # if self.cache[bookshelf_id]: 
        #     # If cache exists and there is no one else in the pool 
        #     # clear the cache also should add a way to save to db.
        #     del self.cache[bookshelf_id]

    async def send_data(self, bookshelf_id: str, data: dict):
        for ws in self.ac.get(bookshelf_id, []):
            await ws.send_json(data)

    async def broadcast(self, bookshelf_id: str):
        for ws in self.ac.get(bookshelf_id, []):
            await ws.send_message('shelf {bookshelf_id} reordered')

    async def reorder_books_and_send_updated_data(self, current_user, bookshelf_id, data, bookshelf_repo:BookshelfCRUDRepositoryGraph):
        _bookshelf = self.cache[bookshelf_id]
        if current_user.bookshelf_id != bookshelf_id:
            await self.send_data(data={"state": "error", 
                "data": self.errors['INVALID_AUTHOR_PERMISSION'] },
                bookshelf_id=bookshelf_id
            )
            return
        
        if current_user.id not in _bookshelf.contributors:
            await self.send_data(data={"state": "error", 
                "data": self.errors['INVALID_AUTHOR_PERMISSION'] },
                bookshelf_id=bookshelf_id
            )
            return

        # try:
        _bookshelf.reorder_book(**data.dict())
        books, book_ids = jsonable_encoder(_bookshelf.get_books())
        response = bookshelf_repo.update_books_in_bookshelf(books=book_ids, bookshelf_id=bookshelf_id)

        if response:
            await self.send_data(data={
                "state": "unlocked", "data": books }, bookshelf_id=bookshelf_id)
        else:
            await self.send_data(data={ "state": "error", 
                "data": self.errors['FAILED_TO_REORDER'] }, bookshelf_id=bookshelf_id)
                
        # except:
        #     await self.send_data(data={
        #         "state": "error", 
        #         "data": self.errors['FAILED_TO_REORDER']
        #     }, bookshelf_id=bookshelf_id)

    async def remove_book_and_send_updated_data(self, current_user, bookshelf_id, data, bookshelf_repo:BookshelfCRUDRepositoryGraph):
        _bookshelf = self.cache[bookshelf_id]
        if current_user.bookshelf_id != bookshelf_id:
            await self.send_data(data={"state": "error", 
                "data": self.errors['INVALID_AUTHOR_PERMISSION'] },
                bookshelf_id=bookshelf_id
            )
            return
        
        if current_user.id not in _bookshelf.contributors:
            await self.send_data(data={"state": "error", 
                "data": self.errors['INVALID_AUTHOR_PERMISSION'] },
                bookshelf_id=bookshelf_id
            )
            return
        
        _bookshelf.remove_book(data.book_id, data.contributor_id)

        books, book_ids = jsonable_encoder(_bookshelf.get_books())

        response = bookshelf_repo.delete_book_from_bookshelf(book_to_remove=data.book_id, books=book_ids, bookshelf_id=bookshelf_id)

        if response:
            await self.send_data(bookshelf_id=bookshelf_id, data={
                "state": "unlocked", "data": books })
        else:
            await self.send_data(data={
                "state": "error", 
                "data": self.errors['FAILED_TO_REORDER']
            }, bookshelf_id=bookshelf_id)

    async def add_book_and_send_updated_data(self, current_user, bookshelf_id, data, bookshelf_repo:BookshelfCRUDRepositoryGraph):
        _bookshelf = self.cache[bookshelf_id]
        if current_user.bookshelf_id != bookshelf_id:
            await self.send_data(data={"state": "error", 
                "data": self.errors['INVALID_AUTHOR_PERMISSION'] },
                bookshelf_id=bookshelf_id
            )
            return
        
        if current_user.id not in _bookshelf.contributors:
            await self.send_data(data={"state": "error", 
                "data": self.errors['INVALID_AUTHOR_PERMISSION'] },
                bookshelf_id=bookshelf_id
            )
            return
        
        response = bookshelf_repo.create_book_in_bookshelf_rel(book_to_add=data.book.id,bookshelf_id=bookshelf_id, user_id=current_user.id)
        if response:
            _bookshelf.add_book_to_shelf(data.book, data.contributor_id)

            books, book_ids = jsonable_encoder(_bookshelf.get_books())

            await self.send_data(bookshelf_id=bookshelf_id, data={
                "state": "unlocked", "data": books })
            
        else:
            await self.send_data(data={
                "state": "error", 
                "data": self.errors['FAILED_TO_REORDER']
            }, bookshelf_id=bookshelf_id)

    async def invalid_data_error(self, bookshelf_id):
        await self.send_data(data={"state": "error", 
            "data": self.errors['INVALID_DATA_ERROR'] },
            bookshelf_id=bookshelf_id
        )

bookshelf_ws_manager = BookshelfWSManager()