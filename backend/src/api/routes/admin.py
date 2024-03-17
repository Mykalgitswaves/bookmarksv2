import fastapi
from fastapi import Depends, HTTPException, Request
from src.database.graph.crud.users import UserCRUDRepositoryGraph
from src.database.graph.crud.books import BookCRUDRepositoryGraph
from src.database.graph.crud.posts import PostCRUDRepositoryGraph
from src.api.utils.database import get_repository
from src.config.config import settings

router = fastapi.APIRouter(prefix="/admin", tags=["admin"])

@router.post("/delete_user_by_username", 
             name="admin:delete_user_by_username")
async def delete_user_by_username(request: Request,
                 user_repo: UserCRUDRepositoryGraph = Depends(get_repository(repo_type=UserCRUDRepositoryGraph))):
    data = await request.json()
    
    username = data.get("username")
    admin_credentials = data.get("admin_credentials")

    if admin_credentials != settings.ADMIN_CREDENTIALS:
        raise fastapi.HTTPException(status_code=403, detail="Forbidden")
    else:
        response = user_repo.delete_user_by_username(username)
        if response:
            return HTTPException(status_code=200, detail="User deleted")
        else:
            return HTTPException(status_code=404, detail="User not found")

@router.post("/delete_book_and_versions_by_google_id", 
             name="admin:delete_book_and_versions_by_google_id")
async def delete_book_and_versions_by_google_id(request: Request,
                            book_repo: BookCRUDRepositoryGraph = Depends(get_repository(repo_type=BookCRUDRepositoryGraph))):
    data = await request.json()
    
    google_id = data.get("google_id")
    admin_credentials = data.get("admin_credentials")
    
    if admin_credentials != settings.ADMIN_CREDENTIALS:
        raise fastapi.HTTPException(status_code=403, detail="Forbidden")
    else:
        response = book_repo.delete_book_and_versions_by_google_id(google_id)
        if response:
            return HTTPException(status_code=200, detail="Book deleted")
        else:
            return HTTPException(status_code=404, detail="Book not found")
        
@router.post("/delete_post_and_comments", 
             name="admin:delete_post_and_comments")
async def delete_post_and_comments(request: Request,
                            post_repo: PostCRUDRepositoryGraph = Depends(get_repository(repo_type=PostCRUDRepositoryGraph))):
    data = await request.json()
    
    post_id = data.get("post_id")
    admin_credentials = data.get("admin_credentials")
    
    if admin_credentials != settings.ADMIN_CREDENTIALS:
        raise fastapi.HTTPException(status_code=403, detail="Forbidden")
    else:
        response = post_repo.delete_post(post_id)
        if response:
            return HTTPException(status_code=200, detail="Post deleted")
        else:
            return HTTPException(status_code=404, detail="Post not found")