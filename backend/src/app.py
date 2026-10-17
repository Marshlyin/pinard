from fastapi import FastAPI

from src.application.exception_handlers import register_exception_handlers
from src.application.routers.bottles_router import router as bottles_router
from src.application.routers.shelves_router import router as shelves_router
from src.application.routers.tag_categories_router import router as tag_categories_router
from src.application.routers.tags_router import router as tags_router
from src.application.spa_static_files import SpaStaticFiles
from src.configuration.logging import create_parent_logger
from src.configuration.settings import Settings

logger = create_parent_logger()


def create_app() -> FastAPI:
    """API seule, routes à la racine (/shelves, /bottles…). Utilisée en développement, le front étant servi par Vite."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(bottles_router)
    app.include_router(shelves_router)
    app.include_router(tag_categories_router)
    app.include_router(tags_router)
    logger.info("Backend de l'application pinard démarré. Glouglouglou !")
    return app


def create_production_app() -> FastAPI:
    """
    Application complète pour la production : l'API sous /api (même chemin qu'avec le proxy Vite en développement,
    documentation sur /api/docs) et le front compilé à la racine. Une seule origine, donc pas de CORS.
    """
    frontend_dist_dir = Settings().frontend_dist_dir
    if frontend_dist_dir is None or not (frontend_dist_dir / "index.html").is_file():
        raise RuntimeError(
            f"Front compilé introuvable dans {frontend_dist_dir} : renseigner PINARD_FRONTEND_DIST_DIR avec le dossier "
            "produit par `npm run build`"
        )

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    # L'ordre compte : /api est testé avant le front, qui intercepte tous les autres chemins
    app.mount("/api", create_app())
    app.mount("/", SpaStaticFiles(directory=frontend_dist_dir, html=True), name="frontend")
    logger.info(f"Front servi depuis {frontend_dist_dir}")
    return app
