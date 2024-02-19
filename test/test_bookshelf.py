import sys
sys.path.append('../')

import models
import pytest
from pydantic import BaseModel
from models import Bookshelf, Node, HashMapDLL
from helpers import timing_decorator
from fastapi import (
    HTTPException,
)

from books_fixture import BOOKS

class BookshelfBook(BaseModel):
    id: str
    bookTitle: str
    author: str
    imgUrl: str

BOOKS = [BookshelfBook(**book) for book in BOOKS]

@pytest.fixture(scope="class")
def setup_class(request):
    request.cls.books = BOOKS
    request.cls.user = 'michaelfinal.png@gmail.com'
    request.cls.shelf_title = '100 favorite books'
    request.cls.shelf_description = 'For your leisure?'
    request.cls.bookshelf = Bookshelf(
        created_by=request.cls.user,
        title=request.cls.shelf_title,
        description=request.cls.shelf_description
    )

@pytest.mark.usefixtures("setup_class")
class TestBookshelf:
    # SHOULD WORK CASES:
        # ✅ 1) If you reorder to the end of a shelf. 
        # ✅ 2) If you reorder to the beginning of a shelf. 
        # ✅ 3) If you delete at the end with multiple books in shelf.
        # ✅ 4) If you delete at the begining with multiple books in shelf.
    
    # SHOULD BREAK CASES:
        # ✅ 1) Try to insert between two non adjacent books.
        # ✅ 2) Try to insert where one of the adjacent books doesnt exist in the linked list.
        # ✅ 3) Try to insert a duplicate book
        # ✅ 4) Reordering to the same position
    def test_can_add_book_to_shelf(self):
        # Grab stringified data from books list
        data = self.books[0]
        # Add book to shelf turns data into a node.
        self.bookshelf.add_book_to_shelf(user_id=self.user, book=data)
        # Should return an array of 1
        assert len(self.bookshelf.books.to_array()) == 1
        books_from_shelf = self.bookshelf.books.to_array()
        # books from shelf should be equal to data initially passed in.
        assert books_from_shelf[0].id == self.books[0].id

        #Deleting
        self.bookshelf.remove_book(author_id=self.user, book_id=data.id)
        assert len(self.bookshelf.books.to_array()) == 0

    def test_reordering_books(self):
        # Adding multiple and reordering.
        for book in self.books:
            self.bookshelf.add_book_to_shelf(book=book, user_id=self.user)
        # first book in list must match self.books ordering
        books_from_shelf = self.bookshelf.get_books()
        assert books_from_shelf[0].id == self.books[0].id
        
        # Take first node in shelf and move it between 3rd and 4th position
        self.bookshelf.reorder_book(
            target_id=self.books[0].id,
            previous_book_id=self.books[2].id,
            next_book_id=self.books[3].id,
            author_id=self.user
        )

        assert self.bookshelf.get_books()[2].id == self.books[0].id

        # 1 reorder to end of list
        self.bookshelf.reorder_book(
            target_id=self.books[0].id,
            previous_book_id=self.books[3].id,
            next_book_id=None,
            author_id=self.user
        )

        assert self.bookshelf.get_books()[3].id == self.books[0].id

        updated_list = self.bookshelf.books.to_array()
        # 2 reorder to the beginning of a shelf
        # Moves Book #1 at the end of list to position 0 at beginning of list.

        self.bookshelf.reorder_book(
            target_id=updated_list[3].id,
            previous_book_id=None,
            next_book_id=updated_list[0].id,
            author_id=self.user
        )

        updated_list = self.bookshelf.get_books()

        assert updated_list[0].id == self.books[0].id
    
    def test_remove_books(self):
        # Try to remove the first book in our list containing multiple books.
        book_list = self.bookshelf.get_books()
        assert len(book_list) == 4
        
        self.bookshelf.remove_book(book_id=book_list[0].id, author_id=self.user)
        updated_list = self.bookshelf.get_books()

        assert len(updated_list) == 3
        # Assert that the updated list has the second element now in the first position.
        assert updated_list[0].id == self.books[1].id

        # Save this before removing to assert that the new last book in list is not this.
        temp_removed_id = updated_list[2].id

        # Remove the last item in the list.
        self.bookshelf.remove_book(book_id=updated_list[2].id, author_id=self.user)
        updated_list = self.bookshelf.get_books()

        assert len(updated_list) == 2
        assert not temp_removed_id == updated_list[1].id

    def test_reorder_non_adjacent_books(self):
        # Start by removing all books from a bookshelf.
        book_ids_to_remove  = [b.id for b in self.bookshelf.get_books()]
        for id in book_ids_to_remove:
            self.bookshelf.remove_book(book_id=id, author_id=self.user)

        assert len(self.bookshelf.get_books()) == 0
        
        # Now re-add all books to bookshelf.
        for book in self.books:
            self.bookshelf.add_book_to_shelf(book=book, user_id=self.user)
        
        refilled_book_shelf = self.bookshelf.get_books()
        assert len(refilled_book_shelf) == 100
        # Should not be able to reorder between two non adjacent books in a dll.
        assert self.bookshelf.reorder_book(
            target_id=refilled_book_shelf[0].id,
            previous_book_id=refilled_book_shelf[1].id,
            next_book_id=refilled_book_shelf[3].id,
            author_id=self.user
        ).status_code == 401

        # Try to reorder where one of the id's doesnt exist in the linked list.
        assert self.bookshelf.reorder_book(
            target_id=refilled_book_shelf[0].id,
            previous_book_id=refilled_book_shelf[1].id,
            next_book_id='5',
            author_id=self.user
        ).status_code == 400
        
    def test_insert_duplicate_book(self):
        books = self.bookshelf.get_books()
        # Should not be able to add the same book twice
        assert self.bookshelf.add_book_to_shelf(
            user_id=self.user,
            book=books[0]
        ).status_code == 400

@pytest.mark.usefixtures("setup_class")
class TestSpeedOfDLL:
    def test_speed_of_get_books(self):
        # Regular implementation of our DLL, no hash map.
        for book in self.books:
            self.bookshelf.add_book_to_shelf(book=book, user_id=self.user)
        
        assert len(self.bookshelf.get_books()) == 100
        # Speed for adding 100 books then retrieving them.

        # Total time taken to add all books: 0.002669 seconds
        # Total time taken to retrieve all books with get_books: 0.000011 seconds to execute

    def test_speed_of_reorder_books(self):
        books = self.bookshelf.get_books()
        # reorder_book took 0.000019 seconds to execute
        # Move to the end
        self.bookshelf.reorder_book(
            target_id=books[99].id,
            previous_book_id=None,
            next_book_id=books[1].id,
            author_id=self.user
        )
        # reorder_book took 0.000021 seconds to execute
        self.bookshelf.reorder_book(
            target_id=books[0].id,
            previous_book_id=books[99].id,
            next_book_id=None,
            author_id=self.user
        )

        # reorder_book took 0.000014 seconds to execute
        self.bookshelf.reorder_book(
            target_id=books[0].id,
            previous_book_id=books[49].id,
            next_book_id=books[50].id,
            author_id=self.user
        )

@pytest.mark.usefixtures("setup_class")
class TestSpeedOfHMDLL:
    BOOKSHELF = None
    def test_speed_of_get_books(self):
        self.BOOKSHELF = Bookshelf(
            created_by=self.user,
            title=self.shelf_title,
            description=self.shelf_description,
            books=HashMapDLL()
        )

        # Although, this is kind of irrelevant - since it isn't likely to happen this fast.
        # 0.682 seconds
        for book in self.books:
            self.BOOKSHELF.add_book_to_shelf(book=book, user_id=self.user)
        
        # get_books took 0.000009 seconds to execute
        books = self.BOOKSHELF.get_books()

        # reorder_book took 0.000003 seconds to execute
        # Move to start.
        self.BOOKSHELF.reorder_book(
            target_id=books[99].id,
            previous_book_id=None,
            next_book_id=books[1].id,
            author_id=self.user
        )
        # reorder_book took 0.000010 seconds to execute
        # Start to end
        self.bookshelf.reorder_book(
            target_id=books[0].id,
            previous_book_id=books[99].id,
            next_book_id=None,
            author_id=self.user
        )

        # reorder_book took 0.000003 seconds to execute
        # Start to middle
        self.bookshelf.reorder_book(
            target_id=books[0].id,
            previous_book_id=books[49].id,
            next_book_id=books[50].id,
            author_id=self.user
        )