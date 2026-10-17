from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.model.tag_category import TagCategory


class TagCategoryRepository(ABC):
    @abstractmethod
    def create(self, category: TagCategory) -> TagCategory:
        pass

    @abstractmethod
    def update(self, category: TagCategory) -> TagCategory:
        pass

    @abstractmethod
    def delete(self, category_id: UUID) -> None:
        """Supprime une catégorie existante et vide (la base refuse la suppression si elle contient des étiquettes)."""

    @abstractmethod
    def find_all(self) -> list[TagCategory]:
        """Toutes les catégories triées par nom."""

    @abstractmethod
    def find_by_id(self, category_id: UUID) -> TagCategory | None:
        pass

    @abstractmethod
    def count_tags(self, category_id: UUID) -> int:
        pass
