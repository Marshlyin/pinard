from fastapi import FastAPI

from src.configuration.logging import create_parent_logger

logger = create_parent_logger()


def create_app() -> FastAPI:
    app = FastAPI()
    logger.info("Backend de l'application pinard démarré. Glouglouglou !")
    return app
