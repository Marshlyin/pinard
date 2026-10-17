from typing import Annotated
from uuid import UUID

from fastapi import Path, status
from fastapi.routing import APIRouter

from src.application.commands.create_shelf_command import CreateShelfCommand
from src.application.commands.update_shelf_command import UpdateShelfCommand
from src.application.mappers import shelf_mapper
from src.application.results.shelf_result import ShelfDetailResult, ShelfResult
from src.configuration.injection_helper import injects
from src.configuration.logging import Logger
from src.domain.services.shelves_service import ShelvesService
from src.transverse.application_constants import DEFAULT_RESPONSES

logger = Logger(child=True)

router = APIRouter(prefix="/shelves", tags=["shelves"], responses=DEFAULT_RESPONSES)


@router.post("", status_code=status.HTTP_201_CREATED, description="Create a new shelf")
def create_shelf(
    command: CreateShelfCommand,
    shelves_service: ShelvesService = injects(ShelvesService),  # noqa: B008
) -> ShelfResult:
    logger.info("Début de l'appel au POST /shelves")
    shelf = shelves_service.create_shelf(shelf_mapper.command_to_domain(command))
    logger.info("Fin de l'appel au POST /shelves")
    return shelf_mapper.domain_to_result(shelf)


@router.get("", description="Get all the shelves (minimal format), sorted by name")
def list_shelves(
    shelves_service: ShelvesService = injects(ShelvesService),  # noqa: B008
) -> list[ShelfResult]:
    logger.info("Début de l'appel au GET /shelves")
    shelves = shelves_service.get_shelves()
    logger.info("Fin de l'appel au GET /shelves")
    return [shelf_mapper.domain_to_result(shelf) for shelf in shelves]


@router.get("/{id}", description="Get the detail of a shelf, with the bottles it contains")
def get_shelf(
    id: Annotated[UUID, Path(title="L'identifiant de l'étagère")],
    shelves_service: ShelvesService = injects(ShelvesService),  # noqa: B008
) -> ShelfDetailResult:
    logger.info(f"Début de l'appel au GET /shelves/{id}")
    shelf = shelves_service.get_shelf(id)
    logger.info(f"Fin de l'appel au GET /shelves/{id}")
    return shelf_mapper.domain_to_detail_result(shelf)


@router.put("/{id}", description="Update the name and the shape of a shelf")
def update_shelf(
    id: Annotated[UUID, Path(title="L'identifiant de l'étagère")],
    command: UpdateShelfCommand,
    shelves_service: ShelvesService = injects(ShelvesService),  # noqa: B008
) -> ShelfResult:
    logger.info(f"Début de l'appel au PUT /shelves/{id}")
    shelf = shelves_service.update_shelf(shelf_mapper.update_command_to_domain(id, command))
    logger.info(f"Fin de l'appel au PUT /shelves/{id}")
    return shelf_mapper.domain_to_result(shelf)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete an empty shelf")
def delete_shelf(
    id: Annotated[UUID, Path(title="L'identifiant de l'étagère")],
    shelves_service: ShelvesService = injects(ShelvesService),  # noqa: B008
) -> None:
    logger.info(f"Début de l'appel au DELETE /shelves/{id}")
    shelves_service.delete_shelf(id)
    logger.info(f"Fin de l'appel au DELETE /shelves/{id}")
