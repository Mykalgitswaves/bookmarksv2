import fastapi
from fastapi import HTTPException, Depends, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated

from src.api.utils.database import get_repository
from src.database.graph.crud.authors import AuthorCRUDRepositoryGraph
from src.models.schemas.authors import Author, AuthorName, AuthorId

router = fastapi.APIRouter(prefix="/authors", tags=["authors"])


@router.get("/{author_id}", name="author:get")
def get_author(
    author_id: str,
    author_repo: AuthorCRUDRepositoryGraph = Depends(
        get_repository(repo_type=AuthorCRUDRepositoryGraph)
    ),
):
    """
    Get a author by id
    """
    result = author_repo.get_author_by_id(author_id=AuthorId(id=author_id).id)
    return JSONResponse(content={"author": jsonable_encoder(result)})


@router.get("/search/{text}", name="author:search2")
def get_authors_by_title(
    text: str,
    skip: int = 0,
    limit: int = 3,
    author_repo: AuthorCRUDRepositoryGraph = Depends(
        get_repository(repo_type=AuthorCRUDRepositoryGraph)
    ),
):
    """
    Search for a author by text
    """
    result = author_repo.search_authors_by_name(
        text=AuthorName(name=text).name, skip=skip, limit=limit
    )
    return result
