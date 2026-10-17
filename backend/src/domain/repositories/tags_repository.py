from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.model.tag import Tag


class TagRepository(ABC):
    @abstractmethod
    def create(self, tag: Tag) -> Tag:
        pass

    @abstractmethod
    def update(self, tag: Tag) -> Tag:
        """Met à jour le nom et la catégorie d'une étiquette existante (les bouteilles étiquetées ne changent pas)."""

    @abstractmethod
    def delete(self, tag_id: UUID) -> None:
        """Supprime l'étiquette et la retire de toutes les bouteilles qui la portent."""

    @abstractmethod
    def find_all(self, category_id: UUID | None = None) -> list[Tag]:
        """Les étiquettes avec leur catégorie, triées par catégorie puis par nom, éventuellement d'une seule catégorie.
        Sans leurs bouteilles."""

    @abstractmethod
    def find_by_ids(self, tag_ids: list[UUID]) -> list[Tag]:
        """Les étiquettes existantes parmi tag_ids, avec leur catégorie (les identifiants inconnus sont ignorés)."""

    @abstractmethod
    def find_by_id(self, tag_id: UUID) -> Tag | None:
        """L'étiquette avec sa catégorie et les bouteilles qui la portent (triées par domaine, cuvée, millésime)."""
