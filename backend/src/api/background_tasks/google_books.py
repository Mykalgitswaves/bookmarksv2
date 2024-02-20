import requests
from fastapi import Depends

from src.api.utils.database import get_repository
from src.database.graph.crud.books import BookCRUDRepositoryGraph
from src.models.schemas.books import Book, BookUpdate
from src.book_apis.google_books.base import GoogleBooks
from src.book_apis.open_library.versions import open_library_versions
from src.book_apis.google_books.pull_books import google_books_pull

class GoogleBooksBackgroundTasks(GoogleBooks):
    def pull_book_and_versions(self,
                               google_book:Book,
                               book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph))):
        google_book = book_repo.create_book(google_book)
        
        if book_repo.check_if_version_or_canon(google_book.id):
            if google_book.isbn13:
                response = open_library_versions.get_book_versions(google_book.isbn13)
            elif google_book.isbn10:
                response = open_library_versions.get_book_versions(google_book.isbn10)
            else:
                response = None

            if response:
                response = response.json()
                if response['numFound'] != 0:
                    versions = response['docs'][0]['isbn']
                    for version in versions:
                        version_book = google_books_pull.pull_google_book_or_add_isbn(str(version), book_repo)
                        if version_book:
                            if version_book.id != google_book.id and book_repo.check_if_version_or_canon(version_book.id):
                                book_repo.create_canon_book_relationship(google_book.id, version_book.id)
                            # else:
                            #     if not book_repo.check_if_version_or_canon(version_book.id):
                            #         logging.warning(f"The book {google_book.book_id} with isbn ({google_book.isbn13},{google_book.isbn10}) had a version conflict with the versions {version_book.id} with isbn ({version_book.isbn13},{version_book.isbn10})")
                                
    def update_book_google_id(self,
                              google_id:str, 
                              book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph))):
        api_key = self.api_key
        db_response = book_repo.get_book_by_google_id(google_id)

        if db_response:    
            path = f"https://www.googleapis.com/books/v1/volumes/{google_id[1:]}?key={api_key}"
            r = requests.get(path)
            response = r.json()
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
                    author_names=None
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
                
                parameters = {
                    "small_img_url":small_img_url,
                    "title":title,
                    "description":description,
                    "isbn13":isbn13,
                    "isbn10":isbn10,
                    "author_names":author_names,
                    "genre_names":genres,
                    "img_url":thumbnail,
                    "pages":pageCount,
                    "publication_year":publishedDate,
                    "lang": language,
                    "google_id": google_id
                }

                book_update = BookUpdate(**parameters)

                book_id = book_repo.update_book_preview(book_update)
                                
                if book_repo.check_if_version_or_canon(book_id):
                    if isbn13:
                        response = open_library_versions.get_book_versions(isbn13)
                    elif isbn10:
                        response = open_library_versions.get_book_versions(isbn10)
                    else:
                        response = None
                        
                    if response:
                        response = response.json()
                        if response['numFound'] != 0:
                            versions = response['docs'][0]['isbn']
                            for version in versions:
                                version_book = google_books_pull.pull_google_book_or_add_isbn(str(version), book_repo)
                                if version_book:
                                    if version_book.id != book_id and book_repo.check_if_version_or_canon(version_book.id):
                                        book_repo.create_canon_book_relationship(book_id, version_book.id)
                                    # else:
                                    #     if not driver.check_if_version_or_canon(version_book.id):
                                    #         logging.warning(f"The book {book_id} with isbn ({isbn13},{isbn10}) had a version conflict with the versions {version_book.id} with isbn ({version_book.isbn13},{version_book.isbn10})")

        #     else:
        #         logging.error(f"API returned no response for book with google id {google_id}")
        #         print(f"API returned no response for book with google id {google_id}")     
        # else:
        #     logging.error(f"Book with google id {google_id} is not in DB as primary key")
                                
google_books_background_tasks = GoogleBooksBackgroundTasks()