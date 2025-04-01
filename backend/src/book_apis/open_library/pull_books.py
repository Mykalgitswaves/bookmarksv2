import requests
import time
from fastapi import Depends

from src.api.utils.database import get_repository
from src.database.graph.crud.books import BookCRUDRepositoryGraph
from src.book_apis.open_library.base import OpenLibrary
from src.config.config import settings
from src.models.schemas.books import Book
from src.api.utils.helpers.books import find_book_by_isbn
from src.utils.logging.logger import logger

class OpenLibraryPull(OpenLibrary):
    def pull_open_library_book(self, 
                         open_lib_id: str, 
                         book_repo: BookCRUDRepositoryGraph = Depends(
                             get_repository(repo_type=BookCRUDRepositoryGraph))
        ):
        """
        Pulls a book from the open library api by id
        """
        logger.info(
            "Pulling book with open lib id",
            extra={
                "open_lib_id": open_lib_id,
                "action": "pull_google_book"}
            )
        db_response = book_repo.get_book_by_open_lib_id(open_lib_id)
        if not db_response:
            true_open_lib_id = open_lib_id[2:]
            path = f"https://openlibrary.org{true_open_lib_id}.json"
            r = requests.get(path)
            if response.status_code != 200:
                logger.error(
                    "Book not found in Open Library",
                    extra={
                        "open_lib_id": open_lib_id,
                        "action": "pull_open_library_book_error"}
                )
                raise Exception(f"ID {open_lib_id} Not Found")
            
            response = r.json()

            if not response:
                logger.error(
                    "Book not found in Open Library",
                    extra={
                        "open_lib_id": open_lib_id,
                        "action": "pull_open_library_book_error"}
                )
                raise Exception(f"ID {open_lib_id} Not Found")

            if true_open_lib_id.startswith("/works"):
                    # Grab the work data
                    book = self.format_work(
                        response,
                        true_open_lib_id
                    )
                    return(book)
            
            elif true_open_lib_id.startswith("/books"):
                    # Grab the edition data
                    book = self.format_edition(
                        response,
                        true_open_lib_id
                    )
                    return(book)        
            
            else:
                logger.error(
                    "Book not found in Open Library",
                    extra={
                        "open_lib_id": open_lib_id,
                        "action": "pull_open_library_book_error"}
                )
                raise Exception(f"ID {open_lib_id} Not Found")
        else:
            return(db_response)
    
    def pull_author_data(
            self,
            author_key: str
    ):
        path = f"https://openlibrary.org{author_key}.json"
        r = requests.get(path)
        if r.status_code != 200:
            return None
        
        response = r.json()
        if response:
            return response.get("name")

    def format_work(
            self,
            response: dict,
            true_open_lib_id: str
    ) -> Book:
        """
        Formats the result of the Works api into a Book object
        """ 
        covers = response.get('covers')
        small_img_url = f"https://covers.openlibrary.org/b/id/{covers[0]}-M.jpg" if covers else None
        thumbnail = f"https://covers.openlibrary.org/b/id/{covers[0]}-L.jpg" if covers else None

        # Get basic book information
        title = response.get('title')
        description = response.get('description')
        
        # Get author information
        author_data = response.get('authors', [])
        author_names = []
        if author_data:
            for author in author_data:
                if isinstance(author, dict) and 'author' in author:
                    author_key = author['author'].get('key')
                    if author_key:
                        author_name = self.pull_author_data(author_key)
                        # Could fetch author name from author_key if needed
                        author_names.append(author_name)
        
        # Get subject/genre information
        genres = response.get('subjects', [])
        
        # Get publication information
        first_publish_date = response.get('first_publish_date')
        number_of_pages = response.get('number_of_pages')
        language = response.get('language', {}).get('key').rsplit("/")[1] if response.get('language') else None
        
        # Get ISBN information (not typically in works API)
        isbn13 = None
        isbn10 = None
        
        book = Book(id = "ow" + true_open_lib_id, 
                    small_img_url=small_img_url,
                    title=title,
                    description=description,
                    isbn13=isbn13,
                    isbn10=isbn10,
                    author_names=author_names,
                    genre_names=genres,
                    img_url=thumbnail,
                    pages=number_of_pages,
                    publication_year=first_publish_date,
                    lang=language,
                    open_lib_id=true_open_lib_id)
        
        logger.info(
            "Book pulled from open library",
            extra={
                "book": book,
                "action": "pull_open_library_result"}
            )
        
        return book
    
    def format_edition(
            self,
            response: dict,
            true_open_lib_id: str
    ) -> Book:
        """
        Formats the result of the Works api into a Book object
        """ 
        covers = response.get('covers')
        small_img_url = f"https://covers.openlibrary.org/b/id/{covers[0]}-M.jpg" if covers else None
        thumbnail = f"https://covers.openlibrary.org/b/id/{covers[0]}-L.jpg" if covers else None

        # Get basic book information
        title = response.get('title')
        description = response.get('description')
        
        # Get author information
        author_data = response.get('authors', [])
        author_names = []
        if author_data:
            for author in author_data:
                if isinstance(author, dict) and 'author' in author:
                    author_key = author['author'].get('key')
                    if author_key:
                        author_name = self.pull_author_data(author_key)
                        # Could fetch author name from author_key if needed
                        author_names.append(author_name)
        
        # Get subject/genre information
        genres = response.get('subjects', [])
        
        # Get publication information
        first_publish_date = response.get('publish_date')
        number_of_pages = response.get('number_of_pages')

        language_record = response.get("languages")[0] if response.get("languages") else None
        language = language_record.get('key').rsplit("/")[1] if language_record else None
        
        # Get ISBN information
        isbn_10_record = response.get("isbn_10")[0] if response.get("isbn_10") else None
        isbn10 = isbn_10_record.get('key').rsplit("/")[1] if isbn_10_record else None

        isbn_13_record = response.get("isbn_13")[0] if response.get("isbn_13") else None
        isbn13 = isbn_13_record.get('key').rsplit("/")[1] if isbn_13_record else None
        
        book = Book(id = "ow" + true_open_lib_id, 
                    small_img_url=small_img_url,
                    title=title,
                    description=description,
                    isbn13=isbn13,
                    isbn10=isbn10,
                    author_names=author_names,
                    genre_names=genres,
                    img_url=thumbnail,
                    pages=number_of_pages,
                    publication_year=first_publish_date,
                    lang=language,
                    open_lib_id=true_open_lib_id)
        
        logger.info(
            "Book pulled from open library",
            extra={
                "book": book,
                "action": "pull_open_library_result"}
            )
        
        return book
        
    def pull_google_book_or_add_isbn(self,
                                     isbn:str, 
                                     book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph)), 
                                     count=0):
        """
        Searches the db for a book by isbn. If it exists its returned, if not it is pulled from google and returned
        """
        db_response = find_book_by_isbn(isbn, book_repo)
        if not db_response:
            path = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            r = requests.get(path)
            responses = r.json()
            if 'items' not in responses:
                if 'error' in responses:
                    # print(responses)
                    # print(isbn)
                    time.sleep(20)
                    count += 1
                    if count >= 5:
                        raise Exception("Timed out conisistently")
                    else:
                        self.pull_google_book_or_add_isbn(isbn, book_repo, count)
                # print(responses)
                # print(isbn)
                return None
            
            for response in responses['items']:
                if 'volumeInfo' in response:
                    if 'industryIdentifiers' in response['volumeInfo']:
                        isbn13 = next((item for item in response['volumeInfo']['industryIdentifiers'] if item["type"] == "ISBN_13"), None)
                        if isbn13:
                            if 'identifier' in isbn13:
                                isbn13 = isbn13['identifier']
                        isbn10 = next((item for item in response['volumeInfo']['industryIdentifiers'] if item["type"] == "ISBN_10"), None)
                        if isbn10:
                            if 'identifier' in isbn10:
                                isbn10 = isbn10['identifier']
                    else:
                        isbn13 = None
                        isbn10 = None
                    
                    if len(isbn) == 10:
                        if isbn != isbn10:
                            continue
                    else:
                        if isbn != isbn13:
                            continue

                    if 'imageLinks' in response['volumeInfo']:
                        if "smallThumbnail" in response['volumeInfo']['imageLinks']:
                            small_img_url=response['volumeInfo']['imageLinks']['smallThumbnail']
                        else:
                            small_img_url=None
                        if "thumbnail" in response['volumeInfo']['imageLinks']:
                            thumbnail=response['volumeInfo']['imageLinks']['thumbnail']
                        else:
                            thumbnail=None
                    else:
                        small_img_url=None
                        thumbnail=None
                    if "title" in response['volumeInfo']:
                        title=response['volumeInfo']['title']

                    else:
                        title=None
                    if 'description' in response['volumeInfo']: 
                        description=response['volumeInfo']['description']
                    else:
                        description=None
                    if 'authors' in response['volumeInfo']: 
                        author_names=response['volumeInfo']['authors']
                    else:
                        author_names=[]
                    if 'categories' in response["volumeInfo"]:
                        genres = response["volumeInfo"]['categories']
                    else:
                        genres = []
                    if 'publishedDate' in response["volumeInfo"]:
                        publishedDate = response["volumeInfo"]['publishedDate']
                    else:
                        publishedDate = None
                    if 'pageCount' in response["volumeInfo"]:
                        pageCount = response["volumeInfo"]['pageCount']
                    else:
                        pageCount = None
                    if 'language' in response["volumeInfo"]:
                        language = response["volumeInfo"]['language']
                    else:
                        language = None
                    
                    book = Book(id = None, 
                                small_img_url=small_img_url,
                                title=title,
                                description=description,
                                isbn13=isbn13,
                                isbn10=isbn10,
                                author_names=author_names,
                                genre_names=genres,
                                img_url=thumbnail,
                                pages=pageCount,
                                publication_year=publishedDate,
                                lang = language,
                                google_id= "g"+response['id'])

                    book = book_repo.create_book(book) 
                    return(book)
                else:
                    raise Exception(f"isbn {isbn} Not Found")
        else:
            return(db_response)

open_library_pull = OpenLibraryPull()
