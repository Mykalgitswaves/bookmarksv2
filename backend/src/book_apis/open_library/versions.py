import requests

from src.book_apis.open_library.base import OpenLibrary

class OpenLibraryVersions(OpenLibrary):
    def get_book_versions(self, isbn: str):
        """
        Pulls all the versions of a book via isbn 13 or isbn 10
        """
        return requests.get(f"{self.base_url}/search.json?q={isbn}&fields=isbn")
    
open_library_versions = OpenLibraryVersions()