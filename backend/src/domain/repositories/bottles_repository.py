from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.model.bottle import Bottle


class BottleRepository(ABC):
    @abstractmethod
    def create(self, bottle: Bottle) -> Bottle:
        """Enregistre la bouteille et ses étiquettes (bottle.tags)."""

    @abstractmethod
    def update(self, bottle: Bottle) -> Bottle:
        """Met à jour cuvée, domaine, millésime et remplace les étiquettes. Les emplacements ne changent pas."""

    @abstractmethod
    def delete(self, bottle_id: UUID) -> None:
        """Supprime la bouteille, ses emplacements et ses liens avec les étiquettes."""

    @abstractmethod
    def find_all(self) -> list[Bottle]:
        """Toutes les bouteilles avec étiquettes et emplacements, triées par domaine, cuvée puis millésime."""

    @abstractmethod
    def find_by_id(self, bottle_id: UUID) -> Bottle | None:
        """La bouteille avec ses étiquettes et ses emplacements."""
