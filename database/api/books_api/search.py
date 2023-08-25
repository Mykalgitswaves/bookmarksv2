import requests
import json
import sys
sys.path.append('./')
from database.db_helpers import Book, Neo4jDriver

class BookSearch():
    def __init__(self):
        with open("config.json","r") as f:
            CONFIG = json.load(f)
        self.api_key = CONFIG['books_api_key']
    def search(self,text):
        """
        Searches the book api without any additional conditions
        """  
        search_results = []
        driver = Neo4jDriver()
        path = f"https://www.googleapis.com/books/v1/volumes?q={text}&key={self.api_key}"
        r = requests.get(path)
        response = r.json()
        for result in response['items']:
            isbn_13 = next((item for item in result['volumeInfo']['industryIdentifiers'] if item["type"] == "ISBN_13"), None)
            book = driver.find_book_by_isnb13(int(isbn_13['identifier']))
            if not book:
                book = Book(result['id'], 
                            small_img_url=result['volumeInfo']['imageLinks']['smallThumbnail'],
                            title=result['volumeInfo']['title'],
                            description=result['volumeInfo']['description'],
                            isbn24=isbn_13['identifier'],
                            author_names=result['volumeInfo']['authors']) 
            search_results.append(book)
        return(search_results)
if __name__ == "__main__":
    search = BookSearch()
    response = search.search("Foundation Asimov")
    print(response)
