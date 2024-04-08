from pydantic import BaseModel, validator
from pydantic.typing import Literal
import datetime
from neo4j.time import DateTime as Neo4jDateTime
from typing import List, Any
from fastapi import HTTPException

from src.utils.exceptions.bookshelves import (
    ReorderException, 
    InvalidDataError, 
    BookAlreadyExists, 
    BookNotInShelf,
    MissingDataError,
    EmptyShelfError,
    InvalidAuthorPermission
)

class BookshelfId(BaseModel):
    id: str

class BookshelfTitle(BookshelfId):
    title: str

class BookshelfDescription(BookshelfId):
    description: str

class BookshelfVisibility(BookshelfId):
    visibility: Literal['public', 'private', 'friends']

class BookshelfUser(BookshelfId):
    user_id: str

class BookshelfContributor(BaseModel):
    user_id: str
    username: str
    profile_img_url: str | None = None
    relationship_to_current_user: str
    created_date: datetime.datetime

    @validator('created_date', pre=True, allow_reuse=True)
    def parse_neo4j_datetime(cls, v):
        if isinstance(v, Neo4jDateTime):
            # Convert Neo4jDateTime to Python datetime
            return v.to_native()
        return v
    
class BookshelfMember(BookshelfContributor):
    pass

class BookshelfCreate(BaseModel):
    title: str
    description: str
    created_by: str
    visibility: Literal['public', 'private', 'friends']
    # created_date: datetime.datetime
    
    # @validator('created_date', pre=True, allow_reuse=True)
    # def parse_neo4j_datetime(cls, v):
    #     if isinstance(v, Neo4jDateTime):
    #         # Convert Neo4jDateTime to Python datetime
    #         return v.to_native()
    #     return v

class BookshelfTaskRoute(BaseModel):
    type: Literal["reorder", "add", "delete"]
    token: str

class BookshelfReorder(BaseModel):
    target_id: str
    previous_book_id: str | None
    next_book_id: str | None
    contributor_id: str

class BookshelfBookRemove(BaseModel):
    book_id: str
    contributor_id: str

class BookshelfBookAdd(BaseModel):
    book: Any
    contributor_id: str

class BookshelfBook(BaseModel):
    id: str
    order: int | None = None
    title: str
    authors: list[str] | None = None
    small_img_url: str | None

class Node:
    def __init__(self, book):
        self.book = book
        self.next = None
        self.prev = None


class DoublyLinkedList:
    def __init__(self):
        self.start_node = None

    # Insert element at the end
    def insert_to_end(self, book) -> None:
        # TODO make this more efficient by implementing it with a hash map.
        if self.start_node is not None:
            current = self.start_node
            while current:
                if current.book.id == book.id:
                    raise BookAlreadyExists
                else:
                    current = current.next

        if self.start_node is None:
            new_node = Node(book=book)
            self.start_node = new_node
            
            return
        
        new_node = Node(book=book)

        n = self.start_node
        if n.book.id == new_node.book.id:
            raise BookAlreadyExists
        # Iterate till the next reaches NULL
        while n.next is not None:
            n = n.next
            if n.book.id == new_node.book.id:
                raise BookAlreadyExists
        n.next = new_node
        new_node.prev = n

    def delete_node(self, book_id):
        # Check if the List is empty
        if self.start_node is None:
            raise BookNotInShelf
        
        n = self.start_node

        # Deletion for one book!
        if n.book.id == book_id and n.next == None:
            self.start_node = None
            return

        # This only works when there is more than one book in shelf
        elif n.book.id == book_id and n.next != None:
            self.start_node = n.next
            self.start_node.prev = None
            return
        
        while n.next is not None:
            n = n.next
            if n.book.id == book_id:
                n.prev.next = n.next
                if n.next:
                    n.next.prev = n.prev
        
                else:
                    pass # Case when tail --> Increase query simplicity
                return
        raise BookNotInShelf
    
    def are_nodes_adjacent(self, prev_node, next_node) -> bool:
        return prev_node.next.book.id == next_node.book.id and next_node.prev.book.id == prev_node.book.id
    
    def is_node_data_valid(self, book_id):
        if book_id is None:
            raise MissingDataError

        if self.start_node is None:
            raise MissingDataError
        
    def reorder_node_to_beginning(self, book_id, next_book_id) -> None:
        self.is_node_data_valid(book_id=book_id)
        print('reordering this shit to the beginning')
    
        if not next_book_id:
            raise MissingDataError

        current = self.start_node

        # Find the node to be reordered
        while current and current.book.id != book_id:
            current = current.next

        if not current:
            raise BookNotInShelf
        
        # If the node is already at the beginning of the list
        if not current.prev:
            return
        
        # Detach the node from its current position
        if current.prev:
            current.prev.next = current.next

        if current.next:
            current.next.prev = current.prev
        
        # Find the node with the next book ID
        next_node = self.start_node
        while next_node:
            if next_node.book.id != next_book_id:
                next_node = next_node.next
            else:
                break
        
        if not next_node:
            print('Next book not found')
            raise BookNotInShelf
        
        # Reorder the node
        current.prev = None
        current.next = next_node
        next_node.prev = current
        self.start_node = current

    def reorder_node_to_end(self, book_id, prev_book_id) -> None:
        self.is_node_data_valid(book_id=book_id)
        
        if not prev_book_id:
            raise MissingDataError

        current = self.start_node

        # Find the node to be reordered
        while current and current.book.id != book_id:
            current = current.next

        if not current:
            print('current not found')
            raise BookNotInShelf
        
        # If the node is already at the end of the list
        # Detach the node from its current position
        if not current.next:
            return
        else:
            current.next.prev = current.prev
        
        # Find the node with the previous book ID
        prev_node = self.start_node
        while prev_node:
            if prev_node.book.id != prev_book_id:
                prev_node = prev_node.next
            else:
                break

        if current.prev:
            current.prev.next = current.next
        else:
            self.start_node = current.next
        
        if not prev_node:
            print('prev node not found')
            raise BookNotInShelf
        
        # Reorder the node
        current.next = None
        current.prev = prev_node
        prev_node.next = current

    def reorder_node(self, book_id, prev_book_id, next_book_id):
        """
        Edge cases to consider:
            1)
                ✅ prev_node_data and next_node_data are not adjacent. This means we are trying to insert between to non adjacent nodes
            2)
                prev_node_data or next_node_data dont exist. This is ok in the instance that we are move to the head OR tail.
            3)
                ✅ node_data doesnt exist
        """
        # Check validation first
        self.is_node_data_valid(book_id=book_id)
        
        # Find the node to be moved
        current = self.start_node
        while current and current.book.id != book_id:
            current = current.next

        if not current:
            print("Current node not found")
            raise BookNotInShelf

        # Node has been found, now handle reordering it to the same position
        # TODO: Double check this, it is likely broken.
        if current.next and current.prev and current.next.book.id == next_book_id and current.prev.book.id == prev_book_id:
            print("Node was moved to the same place")
            raise ReorderException

        # Find the new previous and next nodes
        prev_node = None
        next_node = self.start_node

        if prev_book_id is not None:
            prev_node = self.start_node
            while prev_node and prev_node.book.id != prev_book_id:
                prev_node = prev_node.next

            if not prev_node:
                print('Previous node not found')
                raise BookNotInShelf

        if next_book_id is not None:
            next_node = self.start_node
            while next_node and next_node.book.id != next_book_id:
                next_node = next_node.next

            if not next_node:
                print('Next node not found')
                raise BookNotInShelf

        if not self.are_nodes_adjacent(prev_node, next_node):
            print('Nodes are not adjacent')
            raise ReorderException

         # Detach the node from its current position
        if current.prev:
            current.prev.next = current.next
        else:
            self.start_node = current.next

        if current.next:
            current.next.prev = current.prev

        # PERFORMING THE REORDER STARTING HERE v
        # Place the node at the new position
        current.prev = prev_node
        current.next = next_node

        if prev_node:
            prev_node.next = current
        else:
            self.start_node = current

        if next_node:
            next_node.prev = current
        
    # Traversing and Displaying each element of the list
    def display(self):
        if self.start_node is None:
            raise EmptyShelfError
        else:
            n = self.start_node
            while n is not None:
                print("Element is: ", n.book)
                n = n.next
        print("\n")

    def to_array(self) -> list:
        books = []
        book_ids = []
        current = self.start_node
        index = 0
        while current:
            current.book.order = index
            books.append(current.book)
            book_ids.append(current.book.id)
            index += 1
            current = current.next
        return books, book_ids

class BookshelfQueue(BaseModel):
    instructions: List[dict] = []

    def enqueue(self, data:dict):
        self.instructions.append(data)

    def dequeue(self) -> dict:
        if not self.is_empty():
            return self.instructions.pop(0)
        else:
            raise IndexError("Queue is empty")

    def is_empty(self) -> bool:
        return len(self.instructions) == 0
    
class BookshelfResponse(BaseModel): 
    title: str
    description: str
    books: list[BookshelfBook]
    contributors: list[str]
    followers: list[str]
    visibility: Literal['public', 'private', 'friends']
    members: list[str]
    created_by: str

class BookshelfPreview(BaseModel):
    id: str
    title: str
    description: str
    books_count: int
    book_ids: list[str]
    img_url: str | None = None
    book_img_urls: list[str]
    visibility: Literal['public', 'private', 'friends']
    member_count: int
    created_by: str

class BookshelfPage(BaseModel):
    created_by: str
    title: str
    description: str
    id: str
    img_url: str | None = None
    books: Any
    members: set = set()
    followers: set = set()
    contributors: set = set()
    visibility: Literal['public', 'private', 'friends']
    
class Bookshelf(BaseModel):
    created_by: str
    title: str
    description: str
    id: str
    img_url: str | None = None
    books: Any = DoublyLinkedList()
    members: set = set()
    followers: set = set()
    contributors: set = set()
    visibility: Literal['public', 'private', 'friends']
    queue: Any = BookshelfQueue()

    def add_book_to_shelf(self, book, user_id):
        # Cannot have more than 100 books in your shelf for an arbitrary reason???
        # TODO test how many books possible before performance drop off.
        if user_id in self.contributors:
            return self.books.insert_to_end(book)
        else:
            return HTTPException(500, "Only contributors can add books to bookshelves")
        
    def reorder_book(self, target_id, previous_book_id, next_book_id, contributor_id):
        if contributor_id in self.contributors:
            # Reordering in the middle.
            if previous_book_id and next_book_id:
                return self.books.reorder_node(
                    book_id=target_id,
                    prev_book_id=previous_book_id,
                    next_book_id=next_book_id
                )
            # Reordering to the end. 
            elif previous_book_id != None and next_book_id == None:
                return self.books.reorder_node_to_end(
                    book_id=target_id,
                    prev_book_id=previous_book_id,
                )
            # Reordering to the beginning.
            elif next_book_id != None and previous_book_id == None:
                return self.books.reorder_node_to_beginning(
                    book_id=target_id,
                    next_book_id=next_book_id,
                )
        else:
            raise InvalidAuthorPermission
        
    def remove_book(self, book_id, contributor_id):
        if contributor_id in self.contributors:
            self.books.delete_node(book_id=book_id)
        else: 
            raise InvalidAuthorPermission
          
    def get_books(self):
        return self.books.to_array()
    
    def add_follower(self, user_id):
        self.followers.add(user_id)

    def add_member(self, user_id):
        self.members.add(user_id)
    
    def remove_member(self, user_id):
        self.members.discard(user_id)
    
    def add_contributor(self, user_id):
        # can only be 5 contributors
        if len(self.contributors) > 5:
            return HTTPException(400, "Bookshelves have a maximum of 5 contributors")
        else:
            self.contributors.add(user_id)

    def remove_contributor(self, user_id):
        self.contributors.discard(user_id)

    def dequeue_into_bookshelf(self):
        while not self.queue.is_empty():
            self.reorder_book(**self.queue.dequeue())