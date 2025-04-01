from pydantic import BaseModel
import datetime

class BookId(BaseModel):
    id: str

class BookPreview(BaseModel):
    id: str
    title: str
    small_img_url: str | None = None
    google_id: str | None = None
    author_names: list[str] = []

class BookSearchInput(BaseModel):
    text: str
    skip: int = 0
    limit: int = 3

class BookSearchResult(BaseModel):
    id: str
    title: str
    small_img_url: str | None = None
    publication_year: str | None = None

class BookMetadataSearch(BaseModel):
    book_title: str
    book_authors: list[str]
    
class Book(BaseModel):
    id: str | None
    title: str
    img_url: str | None = None
    small_img_url: str | None = None
    pages: int | None = None
    publication_year: str | None = None
    lang: str | None = None
    description: str | None = None
    isbn13: str | None = None
    isbn10: str | None = None
    genres: list[str] = [] 
    authors: list[str] = []
    tags: list[str] = [] 
    reviews: list[str] = []
    genre_names: list[str] = []
    author_names: list[str] = [] 
    google_id: str | None = None
    open_lib_id: str | None = None

class BookSimilar(BaseModel):
    id: str
    title: str
    img_url: str | None = None

class BookUpdate(BaseModel):
    id: str
    google_id: str
    small_img_url: str | None = None
    title: str | None = None
    description: str | None = None
    isbn13: str | None = None
    isbn10: str | None = None
    author_names: list[str] | None = None
    genres: list[str] | None = None
    img_url: str | None = None
    pages: int | None = None
    publication_year: str | None = None
    lang: str | None = None