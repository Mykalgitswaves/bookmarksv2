import requests
import json

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
                isbn_13 = next((item for item in response['volumeInfo']['industryIdentifiers'] if item["type"] == "ISBN_13"), None)
                if 'identifier' in isbn_13:
                    isbn_13 = int(isbn_13['identifier'])
            else:
                isbn_13 = None
                
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
                "isbn24":isbn_13,
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
                        b.isbn24 = $isbn_13,
                        b.img_url = $img_url,
                        b.lang = $lang,
                        b.originalPublicationYear = $publication_year,
                        b.pages = $pages
                    """
            
            with driver.driver.session() as session:
                session.run(query,parameters)
        else:
            print(f"API returned no response for book with google id {google_id}")     
    else:
        print(f"Book with google id {google_id} is not in DB as primary key")