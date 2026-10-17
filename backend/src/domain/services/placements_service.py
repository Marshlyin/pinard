from uuid import UUID

from injector import inject

from src.configuration.logging import Logger
from src.domain.exceptions.domain_exceptions import (
    BottleNotFoundError,
    PlacementNotFoundError,
    SlotAlreadyOccupiedError,
    SlotOutsideShelfError,
    UnknownShelfError,
)
from src.domain.model.bottle_location import BottleLocation
from src.domain.model.shelf import Shelf
from src.domain.repositories.bottles_repository import BottleRepository
from src.domain.repositories.placements_repository import PlacementRepository
from src.domain.repositories.shelves_repository import ShelfRepository

logger = Logger(child=True)


class PlacementsService:
    """Ranger, déplacer et retirer les exemplaires physiques d'une bouteille dans les étagères."""

    @inject
    def __init__(
        self,
        placement_repository: PlacementRepository,
        bottle_repository: BottleRepository,
        shelf_repository: ShelfRepository,
    ) -> None:
        self.placement_repository = placement_repository
        self.bottle_repository = bottle_repository
        self.shelf_repository = shelf_repository

    def add_placement(self, bottle_id: UUID, shelf_id: UUID, row: int, column: int) -> BottleLocation:
        self._check_bottle_exists(bottle_id)
        shelf = self._get_free_slot_shelf(shelf_id, row, column)

        created = self.placement_repository.create(
            BottleLocation(bottle_id=bottle_id, shelf_id=shelf.id, shelf_name=shelf.name, row=row, column=column)
        )
        logger.info(f"Bouteille {bottle_id} rangée dans '{shelf.name}' (rangée {row}, case {column})")
        return created

    def move_placement(
        self, bottle_id: UUID, placement_id: UUID, shelf_id: UUID, row: int, column: int
    ) -> BottleLocation:
        self._get_placement(bottle_id, placement_id)
        shelf = self._get_free_slot_shelf(shelf_id, row, column, moving_placement_id=placement_id)

        moved = self.placement_repository.update(
            BottleLocation(
                id=placement_id, bottle_id=bottle_id, shelf_id=shelf.id, shelf_name=shelf.name, row=row, column=column
            )
        )
        logger.info(f"Emplacement {placement_id} déplacé dans '{shelf.name}' (rangée {row}, case {column})")
        return moved

    def remove_placement(self, bottle_id: UUID, placement_id: UUID) -> None:
        location = self._get_placement(bottle_id, placement_id)

        self.placement_repository.delete(placement_id)
        logger.info(f"Bouteille {bottle_id} retirée de '{location.shelf_name}' ({location.row}, {location.column})")

    def _check_bottle_exists(self, bottle_id: UUID) -> None:
        if self.bottle_repository.find_by_id(bottle_id) is None:
            raise BottleNotFoundError(bottle_id)

    def _get_placement(self, bottle_id: UUID, placement_id: UUID) -> BottleLocation:
        """L'emplacement doit exister et appartenir à la bouteille de l'URL."""
        self._check_bottle_exists(bottle_id)
        location = self.placement_repository.find_by_id(placement_id)
        if location is None or location.bottle_id != bottle_id:
            raise PlacementNotFoundError(bottle_id, placement_id)
        return location

    def _get_free_slot_shelf(
        self, shelf_id: UUID, row: int, column: int, moving_placement_id: UUID | None = None
    ) -> Shelf:
        """L'étagère cible, après vérification que la case existe et qu'elle est libre (ou occupée par l'emplacement
        en cours de déplacement)."""
        shelf = self.shelf_repository.find_by_id(shelf_id)
        if shelf is None:
            raise UnknownShelfError(shelf_id)

        if not shelf.has_slot(row, column):
            raise SlotOutsideShelfError(shelf.name, shelf.rows, shelf.columns, row, column)

        occupant = shelf.placement_at(row, column)
        if occupant is not None and occupant.id != moving_placement_id:
            raise SlotAlreadyOccupiedError(shelf.name, row, column, occupant.bottle.cuvee, occupant.bottle.domain)
        return shelf
