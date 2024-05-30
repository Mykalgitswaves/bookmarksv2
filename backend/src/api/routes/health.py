import fastapi
from fastapi import HTTPException, Depends, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated
import os

router = fastapi.APIRouter(prefix="/health", tags=["health"])

@router.get("/",
            name="health:health")
def get_server_health():
    """
    Checks for the health file in the backend directory
    """
    if os.path.isfile("health"):
        return JSONResponse(content={"status": "healthy"})
    else: # Return an error
        raise HTTPException(status_code=500, detail="Server is unhealthy")