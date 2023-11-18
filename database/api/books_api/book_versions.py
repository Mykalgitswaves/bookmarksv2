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

if __name__ == "__main__":
    pull_versions("gMWSRNAEACAAJ")