from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.model.shelf import Shelf


class ShelfRepository(ABC):
    @abstractmethod
    def create(self, shelf: Shelf) -> Shelf:
        """Enregistre une nouvelle étagère (son identifiant UUID est déjà généré par le domaine)."""

    @abstractmethod
    def update(self, shelf: Shelf) -> Shelf:
        """Met à jour le nom et la forme d'une étagère existante (ses emplacements ne sont pas modifiés)."""

    @abstractmethod
    def delete(self, shelf_id: UUID) -> None:
        """Supprime une étagère existante et vide (la base refuse la suppression si elle contient des bouteilles)."""

    @abstractmethod
    def find_all(self) -> list[Shelf]:
        """Toutes les étagères triées par nom, sans leurs emplacements."""

    @abstractmethod
    def find_by_id(self, shelf_id: UUID) -> Shelf | None:
        """L'étagère avec ses emplacements occupés (triés par rangée puis case) et leurs bouteilles."""
