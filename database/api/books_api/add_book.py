import requests
import json
import sys
sys.path.append('./')
from database.db_helpers import Book
from helpers import timing_decorator, find_book_by_isbn
import time

@timing_decorator
def pull_google_book(google_id:str, driver):
    with open("config.json","r") as f:
        CONFIG = json.load(f)
    api_key = CONFIG['books_api_key']
    
    db_response = driver.get_book_by_google_id(google_id)
    if not db_response:
        path = f"https://www.googleapis.com/books/v1/volumes/{google_id[1:]}?key={api_key}"
        r = requests.get(path)
        response = r.json()
        if 'volumeInfo' in response:
            if 'industryIdentifiers' in response['volumeInfo']:
                isbn13 = next((item for item in response['volumeInfo']['industryIdentifiers'] if item["type"] == "ISBN_13"), None)
                if 'identifier' in isbn13:
                    isbn13 = isbn13['identifier']
                isbn10 = next((item for item in response['volumeInfo']['industryIdentifiers'] if item["type"] == "ISBN_10"), None)
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
            
            book = Book(None, 
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
                        google_id= "g"+response['id'],
                        in_database=False)
            # book.add_to_db(driver) 
            return(book)
        else:
            raise Exception(f"ID {google_id} Not Found")
    else:
        return(db_response)
    
def pull_google_book_or_add_isbn(isbn:str, driver, count=0):
    """
    Searches the db for a book by isbn. If it exists its returned, if not it is pulled from google and returned
    """
    with open("config.json","r") as f:
        CONFIG = json.load(f)
    api_key = CONFIG['books_api_key']
    
    db_response = find_book_by_isbn(driver,isbn)
    if not db_response:
        path = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        r = requests.get(path)
        responses = r.json()
        if 'items' not in responses:
            if 'error' in responses:
                print(responses)
                print(isbn)
                time.sleep(20)
                count += 1
                if count >= 5:
                    raise Exception("Timed out conisistently")
                else:
                    pull_google_book_or_add_isbn(isbn, driver, count)
            print(responses)
            print(isbn)
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
                
                book = Book(None, 
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
                            google_id= "g"+response['id'],
                            in_database=False)

                book.add_to_db(driver) 
                return(book)
            else:
                raise Exception(f"isbn {isbn} Not Found")
    else:
        return(db_response)
if __name__ == "__main__":
    pull_google_book("gleOXovlXrX0C")