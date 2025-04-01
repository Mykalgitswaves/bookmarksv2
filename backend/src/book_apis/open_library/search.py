import requests
from src.book_apis.open_library.base import OpenLibrary
from src.models.schemas.books import Book

class OpenLibrarySearch(OpenLibrary):
    def search(self, text: str, skip: int, limit: int):
        """
        Searches the book api without any additional conditions
        """ 
        # Empty objects for results
        search_results = []

        # Creates the search request
        base_url = "https://openlibrary.org/search.json"
        search_str = text.lower().replace(" ","+")
        fields_url = "?fields=title,author_name,isbn,cover_i,edition_count,first_publish_year,key,language,number_of_pages_median"
        dynamic_url = f"&q={search_str}&offset={skip}&limit={limit}"
        path = base_url + fields_url + dynamic_url

        # Executes the request
        r = requests.get(path)
        response = r.json()
        # print(response)
        for result in response['docs']:
            # Get basic book info
            title = result.get('title')
            author_names = result.get('author_name', [])

            # Get cover image info
            cover_id = result.get('cover_i')
            small_img_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
            thumbnail = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None

            # Get additional metadata
            isbn13 = None  # OpenLibrary API doesn't directly provide ISBN in search results
            isbn10 = None
            pages = result.get('number_of_pages_median')
            publication_year = result.get('first_publish_year')
            key = result.get('key')

            book = Book(id="ow"+key, 
                        small_img_url=small_img_url,
                        title=title,
                        isbn13=isbn13,
                        isbn10=isbn10,
                        author_names=author_names,
                        img_url=thumbnail,
                        pages=pages,
                        publication_year=publication_year)
            
            search_results.append(book)
            
            if len(search_results) >= limit: # Check if over the limit
                return(search_results)

        return(search_results)
    
open_library_search = OpenLibrarySearch()