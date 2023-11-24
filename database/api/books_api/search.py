import requests
import json
from database.db_helpers import Book, Neo4jDriver

import sys
sys.path.append('./')
from helpers import timing_decorator 

class BookSearch():
    def __init__(self):
        with open("config.json","r") as f:
            CONFIG = json.load(f)
        self.api_key = CONFIG['books_api_key']
    @timing_decorator
    def search(self,text,skip,limit):
        """
        Searches the book api without any additional conditions
        """  
        search_results = []
        search_metadata_map = {}
        driver = Neo4jDriver()
        path = f"https://www.googleapis.com/books/v1/volumes?q={text}&startIndex={skip}&maxResults={limit+round(limit*0.5)}&printType=books&projection=lite&key={self.api_key}"
        r = requests.get(path)
        response = r.json()
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
                    
                if title in search_metadata_map:
                    # if any(item in search_metadata_map[title] for item in author_names): # If any of the authors are matching
                    if set(search_metadata_map[title]) == set(author_names):
                        continue
                
                search_metadata_map.update({title:author_names}) # Update the metadata map
                    
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
                
                search_results.append(book)
                
                if len(search_results) >= limit: # Check if over the limit
                    return(search_results)
        else:
            return([])
        return(search_results)
if __name__ == "__main__":
    search = BookSearch()
    response = search.search("Michael")
    print(response)
