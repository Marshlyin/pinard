from uuid import UUID

from injector import inject

from src.configuration.logging import Logger
from src.domain.exceptions.domain_exceptions import (
    ShelfNameAlreadyExistsError,
    ShelfNotEmptyError,
    ShelfNotFoundError,
    ShelfTooSmallForPlacementsError,
)
from src.domain.model.names import is_same_name
from src.domain.model.shelf import Shelf
from src.domain.repositories.shelves_repository import ShelfRepository

logger = Logger(child=True)


class ShelvesService:
    @inject
    def __init__(self, shelf_repository: ShelfRepository) -> None:
        self.shelf_repository = shelf_repository

    def create_shelf(self, shelf: Shelf) -> Shelf:
        self._check_name_is_free(shelf)

        created = self.shelf_repository.create(shelf)
        logger.info(f"Étagère '{created.name}' créée (id={created.id}, {created.rows}x{created.columns})")
        return created

    def update_shelf(self, shelf: Shelf) -> Shelf:
        existing = self.get_shelf(shelf.id)
        self._check_name_is_free(shelf)

        outside = existing.placements_outside(shelf.rows, shelf.columns)
        if outside:
            raise ShelfTooSmallForPlacementsError(shelf.rows, shelf.columns, len(outside))

        updated = self.shelf_repository.update(shelf)
        logger.info(f"Étagère {updated.id} modifiée : '{updated.name}' ({updated.rows}x{updated.columns})")
        return updated

    def delete_shelf(self, shelf_id: UUID) -> None:
        shelf = self.get_shelf(shelf_id)

        if shelf.placements:
            raise ShelfNotEmptyError(shelf.name, len(shelf.placements))

        self.shelf_repository.delete(shelf_id)
        logger.info(f"Étagère {shelf_id} '{shelf.name}' supprimée")

    def get_shelves(self) -> list[Shelf]:
        return self.shelf_repository.find_all()

    def get_shelf(self, shelf_id: UUID) -> Shelf:
        shelf = self.shelf_repository.find_by_id(shelf_id)
        if shelf is None:
            raise ShelfNotFoundError(shelf_id)
        return shelf

    def _check_name_is_free(self, shelf: Shelf) -> None:
        """Nom unique sans tenir compte de la casse, l'étagère elle-même exceptée (cas d'une modification)."""
        for other in self.shelf_repository.find_all():
            if other.id != shelf.id and is_same_name(other.name, shelf.name):
                raise ShelfNameAlreadyExistsError(shelf.name)
