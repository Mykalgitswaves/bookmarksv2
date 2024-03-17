import fastapi
from fastapi import HTTPException, Depends, BackgroundTasks, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated

from src.models.schemas.users import UserInResponse, User
from src.models.schemas.books import Book, BookSearchInput, BookId, BookMetadataSearch
from src.api.utils.database import get_repository
from src.database.graph.crud.books import BookCRUDRepositoryGraph
from src.securities.authorizations.verify import get_current_active_user
from src.book_apis.google_books.pull_books import google_books_pull
from src.book_apis.google_books.search import google_books_search
from src.api.background_tasks.google_books import google_books_background_tasks

router = fastapi.APIRouter(prefix="/books", tags=["books"])

@router.get("/search/{text}",
            name="book:search2")
def get_books_by_title(text: str,
                       skip: int = 0,
                       limit: int = 3,
                       book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph))):
    """
    Get books by title.
    """
    book_search_input = BookSearchInput(text=text, skip=skip, limit=limit)
    result = book_repo.get_books_by_title(book_search_input.text, book_search_input.skip, book_search_input.limit)
    return(JSONResponse(content={"data": jsonable_encoder(result)}))

@router.get("/{book_id}",
            name="book:get_book")
def get_book_by_id(book_id: str,
                   background_tasks:BackgroundTasks,
                   book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph))):
    """
    Endpoint for book page. If a google id is used, the canonical version of the book is returned
    """
    book_id = BookId(id=book_id)
    if book_id.id[0] == 'g':
        # Checks if the book is already in our database
        book = book_repo.get_book_by_google_id_flexible(book_id.id)
        if not book:
            # Pulls the book down otherwise
            book = google_books_pull.pull_google_book(book_id.id, book_repo)
            background_tasks.add_task(google_books_background_tasks.pull_book_and_versions,book,book_repo)
    else:
        book = book_repo.get_book_by_id(book_id=book_id.id)
        
    return JSONResponse(content={"data": jsonable_encoder(book)})

@router.get("/{book_id}/versions",
            name="book:get_book_versions")
def get_book_versions_from_db(book_id: str,
                              book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph))):
    """
    Endpoint for getting versions of a book from the DB
    """
    if book_id[0] == "g":
        versions = book_repo.get_book_versions_by_google_id(book_id=book_id)
    else:
        versions = book_repo.get_book_versions(book_id=book_id)
    
    return JSONResponse(content={"data": jsonable_encoder(versions)})

@router.get("/{book_id}/versions/metadata",
            name="book:get_book_versions_from_metadata_search")
async def get_book_versions_from_metadata_search(book_id: str, 
                                                 request: Request):
    """
    Endpoint for getting versions of a book from a metadata search
    """
    response = await request.json()
    try:
        book_search = BookMetadataSearch(**response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    versions = google_books_search.search_versions_by_metadata(book_title=book_search.book_title,
                                                               book_authors=book_search.book_authors)
    
    return JSONResponse(content={"data": jsonable_encoder(versions)})

@router.get("/{book_id}/similar",
            name="book:get_similar_books")
def get_similar_books(book_id: str,
                      book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph))):
    """
    Endpoint for similar books
    """
    books = book_repo.get_similar_books(book_id=book_id)
    return JSONResponse(content={"data": jsonable_encoder(books)})