from typing import Annotated
from uuid import UUID

from fastapi import Path, Query, status
from fastapi.routing import APIRouter

from src.application.commands.create_bottle_command import CreateBottleCommand
from src.application.commands.placement_command import PlacementCommand
from src.application.commands.update_bottle_command import UpdateBottleCommand
from src.application.mappers import bottle_mapper
from src.application.results.bottle_result import BottleDetailResult, BottleLocationResult, BottleResult
from src.configuration.injection_helper import injects
from src.configuration.logging import Logger
from src.domain.services.bottles_service import BottlesService
from src.domain.services.placements_service import PlacementsService
from src.transverse.application_constants import DEFAULT_RESPONSES

logger = Logger(child=True)

router = APIRouter(prefix="/bottles", tags=["bottles"], responses=DEFAULT_RESPONSES)

BottleId = Annotated[UUID, Path(title="L'identifiant de la bouteille")]
PlacementId = Annotated[UUID, Path(title="L'identifiant de l'emplacement")]


# --- Bouteilles ---


@router.post("", status_code=status.HTTP_201_CREATED, description="Create a new bottle, with its tags")
def create_bottle(
    command: CreateBottleCommand,
    bottles_service: BottlesService = injects(BottlesService),  # noqa: B008
) -> BottleResult:
    logger.info("Début de l'appel au POST /bottles")
    bottle = bottles_service.create_bottle(bottle_mapper.command_to_domain(command), command.tag_ids)
    logger.info("Fin de l'appel au POST /bottles")
    return bottle_mapper.domain_to_result(bottle)


@router.get(
    "",
    description="Get the bottles with their tags and quantity, sorted by domain, cuvee then vintage. "
    "Filter by tags with tag_id (repeatable): OR between tags of the same category, AND between categories",
)
def list_bottles(
    tag_ids: Annotated[
        list[UUID] | None,
        Query(
            alias="tag_id",
            description="Étiquette à filtrer (répétable). OU entre les étiquettes d'une même catégorie, "
            "ET entre les catégories : ?tag_id=<rouge>&tag_id=<blanc>&tag_id=<longue garde> "
            "→ (rouge OU blanc) ET longue garde",
        ),
    ] = None,
    bottles_service: BottlesService = injects(BottlesService),  # noqa: B008
) -> list[BottleResult]:
    logger.info("Début de l'appel au GET /bottles")
    bottles = bottles_service.get_bottles(tag_ids)
    logger.info("Fin de l'appel au GET /bottles")
    return [bottle_mapper.domain_to_result(bottle) for bottle in bottles]


@router.get("/{id}", description="Get the detail of a bottle, with its tags and where its copies are stored")
def get_bottle(
    id: BottleId,
    bottles_service: BottlesService = injects(BottlesService),  # noqa: B008
) -> BottleDetailResult:
    logger.info(f"Début de l'appel au GET /bottles/{id}")
    bottle = bottles_service.get_bottle(id)
    logger.info(f"Fin de l'appel au GET /bottles/{id}")
    return bottle_mapper.domain_to_detail_result(bottle)


@router.put("/{id}", description="Replace a bottle, tags included (its placements are kept)")
def update_bottle(
    id: BottleId,
    command: UpdateBottleCommand,
    bottles_service: BottlesService = injects(BottlesService),  # noqa: B008
) -> BottleResult:
    logger.info(f"Début de l'appel au PUT /bottles/{id}")
    bottle = bottles_service.update_bottle(bottle_mapper.update_command_to_domain(id, command), command.tag_ids)
    logger.info(f"Fin de l'appel au PUT /bottles/{id}")
    return bottle_mapper.domain_to_result(bottle)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a bottle and all its placements")
def delete_bottle(
    id: BottleId,
    bottles_service: BottlesService = injects(BottlesService),  # noqa: B008
) -> None:
    logger.info(f"Début de l'appel au DELETE /bottles/{id}")
    bottles_service.delete_bottle(id)
    logger.info(f"Fin de l'appel au DELETE /bottles/{id}")


# --- Emplacements des bouteilles physiques ---


@router.post(
    "/{id}/placements", status_code=status.HTTP_201_CREATED, description="Store a copy of the bottle in a shelf slot"
)
def add_bottle_placement(
    id: BottleId,
    command: PlacementCommand,
    placements_service: PlacementsService = injects(PlacementsService),  # noqa: B008
) -> BottleLocationResult:
    logger.info(f"Début de l'appel au POST /bottles/{id}/placements")
    location = placements_service.add_placement(id, command.shelf_id, command.row, command.column)
    logger.info(f"Fin de l'appel au POST /bottles/{id}/placements")
    return bottle_mapper.location_to_result(location)


@router.put("/{id}/placements/{placement_id}", description="Move a copy of the bottle to another slot")
def move_bottle_placement(
    id: BottleId,
    placement_id: PlacementId,
    command: PlacementCommand,
    placements_service: PlacementsService = injects(PlacementsService),  # noqa: B008
) -> BottleLocationResult:
    logger.info(f"Début de l'appel au PUT /bottles/{id}/placements/{placement_id}")
    location = placements_service.move_placement(id, placement_id, command.shelf_id, command.row, command.column)
    logger.info(f"Fin de l'appel au PUT /bottles/{id}/placements/{placement_id}")
    return bottle_mapper.location_to_result(location)


@router.delete(
    "/{id}/placements/{placement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Remove a copy of the bottle from its slot (drunk or taken out)",
)
def remove_bottle_placement(
    id: BottleId,
    placement_id: PlacementId,
    placements_service: PlacementsService = injects(PlacementsService),  # noqa: B008
) -> None:
    logger.info(f"Début de l'appel au DELETE /bottles/{id}/placements/{placement_id}")
    placements_service.remove_placement(id, placement_id)
    logger.info(f"Fin de l'appel au DELETE /bottles/{id}/placements/{placement_id}")
