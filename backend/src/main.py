import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from src.config.config import settings
from src.api.endpoints import router as api_endpoint_router
from src.utils.logging.logger import logger


def initialize_backend_application() -> fastapi.FastAPI:
    app = fastapi.FastAPI()  # type: ignore

    # TODO: Add middleware for CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=settings.IS_ALLOWED_CREDENTIALS,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )

    # TODO: Add event handlers for startup and shutdown.

    app.include_router(router=api_endpoint_router, prefix=settings.API_PREFIX)

    return app


backend_app: fastapi.FastAPI = initialize_backend_application()
logger.info("Backend application initialized", extra={"uri": settings.NEO4J_URI})

if __name__ == "__main__":
    uvicorn.run(
        app="main:backend_app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.RELOAD
    )