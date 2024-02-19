# https://favtutor.com/blogs/doubly-linked-list-python
from fastapi import (
    HTTPException,
)

from database.db_helpers import User
import uuid
import pytest
import datetime
from helpers import timing_decorator
# Delete the element from data
    # We arent using this rn, shouldn't be necessary
    # def InsertToBeginning(self, data) -> None:
    #     new_node = Node(data)
        
    #     if self.start_node is None:
    #         self.start_node = new_node
    #     else:
    #         n = self.start_node 
    #         self.start_node = new_node
    #         self.start_node.next = n
    #         n.prev = self.start_node

# TODO Rename item to book and Node to Item?
class Node:
    def __init__(self, book):
        self.book = book
        self.next = None
        self.prev = None
# Class for doubly Linked List
# TODO change `item` to book_id
        
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
                    return HTTPException(400, "This book is already added")
                else:
                    current = current.next

        if self.start_node is None:
            new_node = Node(book=book)
            self.start_node = new_node
            
            return
        
        new_node = Node(book=book)

        n = self.start_node
        if n.book.id == new_node.book.id:
            return HTTPException(400, 'book already in list')
        # Iterate till the next reaches NULL
        while n.next is not None:
            n = n.next
            if n.book.id == new_node.book.id:
                return HTTPException(400, 'book already in list')
        n.next = new_node
        new_node.prev = n

    def delete_node(self, book_id) -> None:
        # Check if the List is empty
        if self.start_node is None:
            return HTTPException(400, 'book not in list')
        n = self.start_node

        # Deletion for one book!
        if n.book.id == book_id and n.next == None:
            self.start_node = None

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
        return HTTPException(400,'book not in list')
    
    def are_nodes_adjacent(self, prev_node, next_node) -> bool:
        return prev_node.next.book.id == next_node.book.id and next_node.prev.book.id == prev_node.book.id
    
    def is_node_data_valid(self, book_id):
        if book_id is None:
            return HTTPException(401, "Node data is required to reorder")

        if self.start_node is None:
            return HTTPException(400, "The list is empty")
        
    def reorder_node_to_beginning(self, book_id, next_book_id) -> None:
        self.is_node_data_valid(book_id=book_id)
    
        if not next_book_id:
            return HTTPException(400, "No next book id provided")

        current = self.start_node

        # Find the node to be reordered
        while current and current.book.id != book_id:
            current = current.next

        if not current:
            return HTTPException(400, "Node to reorder not found")
        
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
            return HTTPException(400, "The provided next book id wasn't found")
        
        # Reorder the node
        current.prev = None
        current.next = next_node
        next_node.prev = current
        self.start_node = current

    def reorder_node_to_end(self, book_id, prev_book_id) -> None:
        self.is_node_data_valid(book_id=book_id)
        
        if not prev_book_id:
            return HTTPException(400, "No previous book id provided")

        current = self.start_node

        # Find the node to be reordered
        while current and current.book.id != book_id:
            current = current.next

        if not current:
            return HTTPException(400, "Node to reorder not found")
            return
        
        # If the node is already at the end of the list
        if not current.next:
            return
        
        # Detach the node from its current position
        if current.prev:
            current.prev.next = current.next

        if current.next:
            current.next.prev = current.prev
        
        # Find the node with the previous book ID
        prev_node = self.start_node
        while prev_node:
            if prev_node.book.id != prev_book_id:
                prev_node = prev_node.next
            else:
                break
        
        if not prev_node:
            return HTTPException(400, "The provided previous book id wasn't found")
        
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
            return HTTPException(400, "Node to reorder not found")

        # Node has been found, now handle reordering it to the same position
        # TODO: Double check this, it is likely broken.
        if current.next and current.prev and current.next.book.id == next_book_id and current.prev.book.id == prev_book_id:
            return

        # Detach the node from its current position
        if current.prev:
            current.prev.next = current.next
        else:
            self.start_node = current.next

        if current.next:
            current.next.prev = current.prev

        # Find the new previous and next nodes
        prev_node = None
        next_node = self.start_node

        if prev_book_id is not None:
            prev_node = self.start_node
            while prev_node and prev_node.book.id != prev_book_id:
                prev_node = prev_node.next

            if not prev_node:
                return HTTPException(400, "Previous node not found")

        if next_book_id is not None:
            next_node = self.start_node
            while next_node and next_node.book.id != next_book_id:
                next_node = next_node.next

            if not next_node:
                return HTTPException(400, "next node not found")
     
        if not self.are_nodes_adjacent(prev_node, next_node):
            return HTTPException(401, "Reordered nodes must be adjacent")
        
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
            return HTTPException(400, "The list is empty")
        else:
            n = self.start_node
            while n is not None:
                print("Element is: ", n.book)
                n = n.next
        print("\n")

    def to_array(self) -> list:
        books = []
        current = self.start_node
        while current:
            books.append(current.book)
            current = current.next
        return books
    
"""
    Bookshelves rely on a DoublyLinkedList implementation to handle logic. 
    data (a book) being sent to a bookshelf for an insertion should look like this:

        book = {
            name: str,
            book_title: str,
            author: [str],
            imgUrl: str
        }

    When we reorder we need to send references to previous nodes and next nodes and the current node we want to see?

    # TODO test that size actually works on DoublyLinkedList implementation.
    # TODO test that this shit is actually doable.
"""
# Possible optimization of first one.
class HashMapDLL:
    def __init__(self):
        self.start_node = None
        self.node_map = {}

    def insert_to_end(self, book) -> None:
        if book.id in self.node_map:
            raise HTTPException(400, "This book is already added")
        
        new_node = Node(book=book)
        if self.start_node is None:
            self.start_node = new_node
        else:
            current = self.start_node
            while current.next:
                current = current.next
            current.next = new_node
            new_node.prev = current
        
        self.node_map[book.id] = new_node

    def delete_node(self, book_id) -> None:
        if book_id not in self.node_map:
            raise HTTPException(400, 'Book not in list')

        node_to_delete = self.node_map[book_id]
        if node_to_delete.prev:
            node_to_delete.prev.next = node_to_delete.next
        else:
            self.start_node = node_to_delete.next

        if node_to_delete.next:
            node_to_delete.next.prev = node_to_delete.prev

        del self.node_map[book_id]

    def reorder_node_to_beginning(self, book_id, next_book_id):
        # If next_book_id is not provided, the node will be moved to the start of the list
        self.is_node_data_valid(book_id=book_id)
    
        if not next_book_id:
            return HTTPException(400, "No next book id provided")

        current = self.node_map[book_id]

        if not current:
            return HTTPException(400, "Node to reorder not found")
        
        # If the node is already at the beginning of the list
        if not current.prev:
            return
        
        # Detach the node from its current position
        if current.prev:
            current.prev.next = current.next

        if current.next:
            current.next.prev = current.prev
        
        # Find the node with the next book ID
        next_node = self.node_map.get(next_book_id)
        
        if not next_node:
            return HTTPException(400, "The provided next book id wasn't found")
        
        # Reorder the node
        current.prev = None
        current.next = next_node
        next_node.prev = current
        self.start_node = current

    def reorder_node_to_end(self, book_id, prev_book_id):
        # If prev_book_id is not provided, the node will be moved to the end of the list
        
        if not prev_book_id:
            return HTTPException(400, "No previous book id provided")

        current = self.node_map[book_id]


        if not current:
            return HTTPException(400, "Node to reorder not found")
                
        # If the node is already at the end of the list
        if not current.next:
            return
        
        # Detach the node from its current position
        if current.prev:
            current.prev.next = current.next

        if current.next:
            current.next.prev = current.prev
        
        # Find the node with the previous book ID
        prev_node = self.node_map.get(prev_book_id)
        
        if not prev_node:
            return HTTPException(400, "The provided previous book id wasn't found")
        
        # Reorder the node
        current.next = None
        current.prev = prev_node
        prev_node.next = current

    def reorder_node(self, book_id, prev_book_id, next_book_id):
        if book_id not in self.node_map:
            raise HTTPException(400, "Node to reorder not found")
        
        current_node = self.node_map[book_id]

        if prev_book_id:
            prev_node = self.node_map.get(prev_book_id)
            if not prev_node:
                raise HTTPException(400, "Previous node not found")
            if prev_node.next != current_node:
                raise HTTPException(401, "Reordered nodes must be adjacent")
        else:
            prev_node = None

        if next_book_id:
            next_node = self.node_map.get(next_book_id)
            if not next_node:
                raise HTTPException(400, "Next node not found")
            if next_node.prev != current_node:
                raise HTTPException(401, "Reordered nodes must be adjacent")
        else:
            next_node = None

        if prev_node:
            prev_node.next = current_node.next
        else:
            self.start_node = current_node.next

        if next_node:
            next_node.prev = current_node.prev

        if current_node.next:
            current_node.next.prev = prev_node
        if current_node.prev:
            current_node.prev.next = next_node

        current_node.prev = next_node
        current_node.next = prev_node

    def are_nodes_adjacent(self, prev_node, next_node) -> bool:
        return prev_node.next == next_node and next_node.prev == prev_node

    def is_node_data_valid(self, book_id):
        if book_id is None:
            raise HTTPException(401, "Node data is required to reorder")

        if book_id not in self.node_map:
            raise HTTPException(400, "The node is not in the list")

    def display(self):
        if self.start_node is None:
            raise HTTPException(400, "The list is empty")
        else:
            current = self.start_node
            while current:
                print("Element is: ", current.book)
                current = current.next
        print("\n")

    def to_array(self) -> list:
        books = []
        current = self.start_node
        while current:
            books.append(current.book)
            current = current.next
        return books





class Bookshelf():
    def __init__(
        self, created_by: str, title: str, description: str, books=None
    ) -> None:
        self.created_by = created_by
        self.title = title
        self.description = description
        self.id = str(uuid.uuid4())
        self.image_url: str
        self.books = DoublyLinkedList() if books is None else books
        self.followers = set() # list of str's id.
        self.authors = set() # list of str's id.
        # Need this dude
        self.authors.add(self.created_by)

    @timing_decorator
    def add_book_to_shelf(self, book, user_id):
        # Cannot have more than 100 books in your shelf for an arbitrary reason???
        # TODO test how many books possible before performance drop off.
        if user_id in self.authors:
            return self.books.insert_to_end(book)
        else:
            return HTTPException(500, "Only authors can add books to bookshelves")
        
    @timing_decorator
    def reorder_book(self, target_id, previous_book_id, next_book_id, author_id):
        if author_id in self.authors:
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
            return HTTPException(400, "Only authors can reorder bookshelves")
        
    @timing_decorator
    def remove_book(self, book_id, author_id):
        if author_id in self.authors:
            self.books.delete_node(book_id=book_id)
        else: 
            return HTTPException(500, "Must be an author to delete books from a shelf")
        
    @timing_decorator  
    def get_books(self):
        return self.books.to_array()
    
    def add_follower(self, user_id):
        self.followers.add(user_id)
    
    def add_author(self, user_id):
        # can only be 5 authors
        if len(self.authors) > 5:
            return HTTPException(400, "Bookshelves have a maximum of 5 authors")
        else:
            self.authors.add(user_id)

    def remove_author(self, user_id):
        self.authors.discard(user_id)


"""
I have a list: [
{
        id: '1',
        order: 0,
        bookTitle: 'Brave New World',
        author: "Aldous Huxley",
        imgUrl: "http://books.google.com/books/content?id=TIJ5EAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
    },
    {
        id: '2',
        order: 1,
        bookTitle: 'Infinite Jest',
        author: "David Foster Wallace",
        imgUrl: 'http://upload.wikimedia.org/wikipedia/en/4/4f/Infinite_jest_cover.jpg',
    },
    {
        id: '3',
        order: 2,
        bookTitle: 'The sirens of Titan',
        author: "Kurt Vonnegut",
        imgUrl: 'http://pictures.abebooks.com/isbn/9780385333498-us.jpg',
    },
    {
        id: '4',
        order: 3,
        bookTitle: 'The Odyssey',
        author: "Homer",
        imgUrl: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Giuseppe_Bottani_-_Athena_revealing_Ithaca_to_Ulysses.jpg/440px-Giuseppe_Bottani_-_Athena_revealing_Ithaca_to_Ulysses.jpg',
    }
]

IN RETROSPECT THIS WAS RLLY DUMB DISREGARD.

I reorder id #1 to the id#4 position (moving whats at index 0 to whats at index 3), can i do this with our current ds. The answer is NO. Nodes should not have to be adjacent for us to reorder. By using a Map (or dict in the case of python) we can have reordering at constant time.

from collections import OrderedDict
import asyncio
# Note this implementation relies on having the size of the bookshelf.

class BooksMap():
    def __init__(self):
       self.books = {}
       self.size = 0
       self.is_removing = False

    def add_book_to_map(self, book):
        # You need a book dude.
        assert book is not None
        # If the map has no books
        if self.size == 0:
            self.books[0] = book
            self.size += 1
        # How to add a book to the end of the dict
        else:
            self.books[self.size + 1] = book
            self.size += 1

    def reorder_books(self, book_1, book_2):
        # Do book 1 and book 2 exist and are they in self.books?
        # Are book_1 and book_2 the same book? If so, do nothing.
        while self.is_removing == True:

        if book_1 and book_2 == None:
            raise("400", "Can't reorder fake books dude.")
        
        if self.books[book_1.order] or self.books[book_2.order] == None:
            raise("400", "Books need to exist to reorder.")
        
        if book_1.order == book_2.order:
            return
        
        book_2_temp = book_2
        self.books[book_2.order] = book_1
        self.books[book_1.order] = book_2_temp

    def remove_book(self, book):
        # lock, remove, reshuffle, then unlock
        self.is_removing = True
        
        del self.books[book.order]
        self.size -= 1
        self.books = OrderedDict(sorted(self.books.items(), key=lambda book: book[0]))

        self.is_removing = False
"""