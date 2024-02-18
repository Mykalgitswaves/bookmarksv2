import sys
sys.path.append('../')

import models
import pytest
from pydantic import BaseModel
from models import Bookshelf, Node

"""
class BookshelfTest():
    # Constants to use in diff tests.
    BOOKSHELF = None
    USER_1 = 'CASHMONEY_1'
    USER_2 = 'CASHMONEY_2'
    BOOK = {
            'order': 1,
            'id': 'G42069_NICE',
            'book_title': "Infinite Jest",
            'author': ['David Foster Wallace'],
            'imgUrl': ''
        }
    def test_populate_empty_bookshelf():

        Create an empty bookshelf without any books. ensure that you can add a book to a bookshelf, add an author, remove an author, add a follower, remove a follower. 
            Only an author can add books to a shelf

        BOOKSHELF = Bookshelf(

        )
    def test_add_books_to_shelf_and_reorder():

        Populate a bookshelf and try to reorder books on it. 

    def get_books_from_shelf():



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
"""

BOOKS = [
{
        'id': '1',
        'bookTitle': 'Brave New World',
        'author': "Aldous Huxley",
        'imgUrl': "http://books.google.com/books/content?id=TIJ5EAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
    },
    {
        'id': '2',
        'bookTitle': 'Infinite Jest',
        'author': "David Foster Wallace",
        'imgUrl': 'http://upload.wikimedia.org/wikipedia/en/4/4f/Infinite_jest_cover.jpg',
    },
    {
        'id': '3',
        'bookTitle': 'The sirens of Titan',
        'author': "Kurt Vonnegut",
        'imgUrl': 'http://pictures.abebooks.com/isbn/9780385333498-us.jpg',
    },
    {
        'id': '4',
        'bookTitle': 'The Odyssey',
        'author': "Homer",
        'imgUrl': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Giuseppe_Bottani_-_Athena_revealing_Ithaca_to_Ulysses.jpg/440px-Giuseppe_Bottani_-_Athena_revealing_Ithaca_to_Ulysses.jpg',
    }
]

class BookshelfBook(BaseModel):
    id: str
    bookTitle: str
    author: str
    imgUrl: str

BOOKS = [BookshelfBook(**book) for book in BOOKS]



@pytest.fixture(scope="class")
def setup_class(request):
    request.cls.books = BOOKS
    request.cls.bookshelf = None
    request.cls.user = 'michaelfinal.png@gmail.com'
    request.cls.shelf_title = '100 favorite books'
    request.cls.shelf_description = 'For your leisure?'

@pytest.mark.usefixtures("setup_class")
class TestBookshelf:
    def test_can_add_book_to_shelf(self):
        self.bookshelf = Bookshelf(
            created_by=self.user,
            title=self.shelf_title,
            description=self.shelf_description
        )
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
        
        # SHOULD WORK CASES:
        # ✅ 1) If you reorder to the end of a shelf. 
        # ✅ 2) If you reorder to the beginning of a shelf. 
        # 3) If you delete at the end with multiple books in shelf.
        # 4) If you delete at the begining with multiple books in shelf.

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

        assert self.bookshelf.get_books()[0].id == self.books[0].id

        # SHOULD BREAK CASES:
        # 1) Try to insert between two non adjacent books.
        # 2) Try to insert where one of the adjacent books doesnt exist in the linked list.
        # 3) Try to insert a duplicate book
        # 4) Reordering to the same position

    