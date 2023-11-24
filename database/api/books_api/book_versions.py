import requests
import json

import sys
sys.path.append('./')
from database.db_helpers import Book, Neo4jDriver
from helpers import timing_decorator 

with open("config.json","r") as f:
    CONFIG = json.load(f)
api_key = CONFIG['books_api_key']

# versions_endpoint = f"https://openlibrary.org/search.json?q={isbn}&fields=isbn"
# google_isbn_endpoint = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={api_key}"



def pull_versions(isbn:str):
    """
    Pulls all the versions of a book via isbn 13 or isbn 10
    """
    return requests.get(f"https://openlibrary.org/search.json?q={isbn}&fields=isbn")

def search_versions_by_metadata(book_title:str,book_authors:list):
    """
    Searches the books api for versions of the same book
    """
    version_results = []
    result = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=intitle:"{book_title}"&projection=lite&maxResults=20')
    if result:
        response = result.json()
        # print(response)
        if response["totalItems"] > 0:
            for result in response['items']:
                if "title" in result['volumeInfo']:
                    title=result['volumeInfo']['title']
                    # print(title)
                else:
                    title=None
                    
                if 'authors' in result['volumeInfo']: 
                    author_names=result['volumeInfo']['authors']
                else:
                    author_names=None
                    
                if set(author_names) != set(book_authors):
                    continue
                    
                if 'industryIdentifiers' in result['volumeInfo']:
                    isbn13 = next((item for item in result['volumeInfo']['industryIdentifiers'] if item["type"] == "ISBN_13"), None)
                    isbn10 = next((item for item in result['volumeInfo']['industryIdentifiers'] if item["type"] == "ISBN_10"), None)
                    if isbn13:
                        isbn13 = isbn13['identifier']
                    else:
                        print(result['volumeInfo']['industryIdentifiers'])
                    if isbn10:
                        isbn10=isbn10['identifier']
                else:
                    isbn13 = None
                    isbn10 = None

                if 'imageLinks' in result['volumeInfo']:
                    if "smallThumbnail" in result['volumeInfo']['imageLinks']:
                        small_img_url=result['volumeInfo']['imageLinks']['smallThumbnail']
                    else:
                        small_img_url=None
                    if "thumbnail" in result['volumeInfo']['imageLinks']:
                        thumbnail=result['volumeInfo']['imageLinks']['thumbnail']
                    else:
                        thumbnail=None
                else:
                    small_img_url=None
                    thumbnail=None
                if 'description' in result['volumeInfo']: 
                    description=result['volumeInfo']['description']
                else:
                    description=None
                if 'categories' in result["volumeInfo"]:
                    genres = result["volumeInfo"]['categories']
                else:
                    genres = []
                if 'publishedDate' in result["volumeInfo"]:
                    publishedDate = result["volumeInfo"]['publishedDate']
                else:
                    publishedDate = None
                if 'pageCount' in result["volumeInfo"]:
                    pageCount = result["volumeInfo"]['pageCount']
                else:
                    pageCount = None
                

                book = Book("g"+result['id'], 
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
                            in_database=False)
                
                version_results.append(book)
                
    return version_results

if __name__ == "__main__":
    pull_versions("gMWSRNAEACAAJ")