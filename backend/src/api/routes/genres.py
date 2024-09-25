import fastapi
from fastapi import HTTPException, Depends, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated

from src.api.utils.database import get_repository
from src.database.graph.crud.genres import GenreCRUDRepositoryGraph
from src.models.schemas.genres import GenreName

router = fastapi.APIRouter(prefix="/genres", tags=["genres"])


@router.get("/search/{text}", name="genre:search2")
def get_genres_by_title(
    text: str,
    skip: int = 0,
    limit: int = 3,
    genre_repo: GenreCRUDRepositoryGraph = Depends(
        get_repository(repo_type=GenreCRUDRepositoryGraph)
    ),
):
    """
    Search for a genre by text
    """
    result = genre_repo.search_genres_by_name(
        text=GenreName(name=text).name, skip=skip, limit=limit
    )
    return result
