from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.configuration.logging import Logger
from src.domain.exceptions.domain_exceptions import DomainError, ResourceNotFoundError

logger = Logger(child=True)


async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
    logger.warning(f"Erreur fonctionnelle {exc.code} : {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"code": exc.code, "message": exc.message},
    )


async def resource_not_found_error_handler(_request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    logger.info(f"Ressource non trouvée {exc.code} : {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"code": exc.code, "message": exc.message},
    )


async def request_validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    # FastAPI renvoie 422 par défaut : on réserve 422 aux erreurs fonctionnelles, 400 pour les paramètres invalides
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": "INVALID_PARAMETERS",
            "message": "Paramètres en entrée invalides",
            "details": jsonable_encoder(exc.errors()),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    # Starlette choisit le handler le plus spécifique (MRO) : ResourceNotFoundError → 404, autres DomainError → 422
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(ResourceNotFoundError, resource_not_found_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
