from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.model.bottle_location import BottleLocation


class PlacementRepository(ABC):
    @abstractmethod
    def create(self, location: BottleLocation) -> BottleLocation:
        pass

    @abstractmethod
    def update(self, location: BottleLocation) -> BottleLocation:
        """Déplace un emplacement existant (étagère, rangée, case)."""

    @abstractmethod
    def delete(self, placement_id: UUID) -> None:
        pass

    @abstractmethod
    def find_by_id(self, placement_id: UUID) -> BottleLocation | None:
        pass
