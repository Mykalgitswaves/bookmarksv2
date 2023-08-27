import requests
import json
import sys
sys.path.append('./')
from database.db_helpers import Book, Neo4jDriver
from helpers import timing_decorator 

class BookSearch():
    def __init__(self):
        with open("config.json","r") as f:
            CONFIG = json.load(f)
        self.api_key = CONFIG['books_api_key']
    @timing_decorator
    def search(self,text):
        """
        Searches the book api without any additional conditions
        """  
        search_results = []
        driver = Neo4jDriver()
        path = f"https://www.googleapis.com/books/v1/volumes?q={text}&key={self.api_key}"
        r = requests.get(path)
        response = r.json()
        if response["totalItems"] > 0:
            for result in response['items']:
                if 'industryIdentifiers' in result['volumeInfo']:
                    isbn_13 = next((item for item in result['volumeInfo']['industryIdentifiers'] if item["type"] == "ISBN_13"), None)
                    if not isbn_13:
                        continue
                    book = driver.find_book_by_isnb13(int(isbn_13['identifier']))
                    if not book:
                        if "smallThumbnail" in result['volumeInfo']['imageLinks']:
                            small_img_url=result['volumeInfo']['imageLinks']['smallThumbnail']
                        else:
                            small_img_url=None
                        if "title" in result['volumeInfo']: 
                            title=result['volumeInfo']['title']
                        else:
                            title=None
                        if 'description' in result['volumeInfo']: 
                            description=result['volumeInfo']['description']
                        else:
                            description=None
                        if 'authors' in result['volumeInfo']: 
                            author_names=result['volumeInfo']['authors']
                        else:
                            author_names=None
                        if 'categories' in result["volumeInfo"]:
                            genres = result["volumeInfo"]['categories']
                        else:
                            genres = []
                        if 'publishedDate' in result["volumeInfo"]:
                            publishedDate = result["volumeInfo"]['publishedDate']
                        else:
                            publishedDate = []
                        if 'pageCount' in result["volumeInfo"]:
                            pageCount = result["volumeInfo"]['pageCount']
                        else:
                            pageCount = []
                        if "thumbnail" in result['volumeInfo']['imageLinks']:
                            thumbnail=result['volumeInfo']['imageLinks']['thumbnail']
                        else:
                            thumbnail=None
                        


                        book = Book(result['id'], 
                                    small_img_url=small_img_url,
                                    title=title,
                                    description=description,
                                    isbn24=isbn_13['identifier'],
                                    author_names=author_names,
                                    genre_names=genres,
                                    img_url=thumbnail,
                                    pages=pageCount,
                                    publication_year=publishedDate,
                                    in_database=False) 
                    search_results.append(book)
                    
        else:
            return([])
        return(search_results)
if __name__ == "__main__":
    search = BookSearch()
    response = search.search("Michael")
    print(response)
