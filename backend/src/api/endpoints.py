import fastapi

from src.api.routes.admin import router as admin_router
from src.api.routes.authentication import router as authentication_router
from src.api.routes.authors import router as authors_router
from src.api.routes.books import router as books_router
from src.api.routes.bookshelves import router as bookshelves_router
from src.api.routes.genres import router as genres_router
from src.api.routes.health import router as health_router
from src.api.routes.posts import router as posts_router
from src.api.routes.search import router as search_router
from src.api.routes.setup_user import router as setup_user_router
from src.api.routes.user import router as user_router

router = fastapi.APIRouter()

router.include_router(router=admin_router)
router.include_router(router=authentication_router)
router.include_router(router=authors_router)
router.include_router(router=books_router)
router.include_router(router=bookshelves_router)
router.include_router(router=genres_router)
router.include_router(router=health_router)
router.include_router(router=posts_router)
router.include_router(router=setup_user_router)
router.include_router(router=search_router)
router.include_router(router=user_router)