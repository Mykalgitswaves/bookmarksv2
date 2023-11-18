import requests
import json
from database.api.books_api import book_versions, add_book

from database.db_helpers import (
    Book
)

with open("config.json","r") as f:
        CONFIG = json.load(f)


def update_book_google_id(google_id:str, driver):
    api_key = CONFIG['books_api_key']
    db_response = driver.get_book_by_google_id(google_id)

    if db_response:    
        path = f"https://www.googleapis.com/books/v1/volumes/{google_id[1:]}?key={api_key}"
        r = requests.get(path)
        response = r.json()
        if 'volumeInfo' in response:
            if 'industryIdentifiers' in response['volumeInfo']:
                isbn13 = next((item for item in response['volumeInfo']['industryIdentifiers'] if item["type"] == "ISBN_13"), None)
                if 'identifier' in isbn13:
                    isbn13 = int(isbn13['identifier'])
                isbn10 = next((item for item in response['volumeInfo']['industryIdentifiers'] if item["type"] == "ISBN_10"), None)
                if 'identifier' in isbn10:
                    isbn10 = int(isbn10['identifier'])
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
                "lang ": language,
                "google_id": google_id
            }
        
            
            query = """
                    match (b:Book {id:$google_id})
                    set b.id = randomUUID(),
                        b.google_id = $google_id,
                        b.description = $description,
                        b.isbn13 = $isbn13,
                        b.isbn10 = $isbn10
                        b.img_url = $img_url,
                        b.lang = $lang,
                        b.originalPublicationYear = $publication_year,
                        b.pages = $pages
                    """
            
            with driver.driver.session() as session: # This looks wrong
                session.run(query,parameters)
        else:
            print(f"API returned no response for book with google id {google_id}")     
    else:
        print(f"Book with google id {google_id} is not in DB as primary key")

def pull_book_and_versions(google_book:Book, driver):
    google_book.add_to_db(driver)

    if driver.check_if_version_or_canon(google_book.id):
        if google_book.isbn13:
            response = book_versions.pull_versions(google_book.isbn13)
        elif google_book.isbn10:
            response = book_versions.pull_versions(google_book.isbn10)
        else:
            response = None

        if response:
            response = response.json()
            if response['numFound'] != 0:
                versions = response['docs'][0]['isbn']
                for version in versions:
                    version_book = add_book.pull_google_book_or_add_isbn(str(version), driver)
                    if version_book:
                        if version_book.id != google_book.id and driver.check_if_version_or_canon(version_book.id):
                            version_book.add_canon_version(google_book.id, driver)
