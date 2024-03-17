import fastapi
from fastapi import HTTPException, Depends, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated

from src.api.utils.database import get_repository
from src.database.graph.crud.search import SearchCRUDRepositoryGraph
from src.models.schemas.search import SearchSchema
from src.book_apis.google_books.search import google_books_search

router = fastapi.APIRouter(prefix="/search", tags=["search"])

@router.get("/{param}",
            name="search:full")
def search_for_param(param: str, 
                     skip: int=0, 
                     limit: int=5,
                     search_repo: SearchCRUDRepositoryGraph = Depends(get_repository(repo_type=SearchCRUDRepositoryGraph))):
    """
    Endpoint used for searching for users, todo add in credentials for searching
    """
    
    books_result = google_books_search.search(param, skip, limit)
    search_result = search_repo.search_for_param(param=param, skip=skip, limit=limit)
    search_result['books'] = books_result

    return JSONResponse(content={"data": jsonable_encoder(search_result)})

@router.get("/book/{param}",
            name="search:books")
def search_for_param(param: str, 
                     skip: int=0, 
                     limit: int=5):
    """
    Endpoint used for searching for users, todo add in credentials for searching
    """
    
    books_result = google_books_search.search(param, skip, limit)

    return JSONResponse(content={"data": jsonable_encoder(books_result)})