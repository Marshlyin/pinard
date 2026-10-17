from injector import inject

from src.domain.model.bottle_placement import BottlePlacement
from src.domain.model.shelf import Shelf
from src.infrastructure.entity.bottle_placement_entity import BottlePlacementEntity
from src.infrastructure.entity.shelf_entity import ShelfEntity
from src.infrastructure.mappers.bottle_entity_mapper import BottleEntityMapper


class ShelfEntityMapper:
    @inject
    def __init__(self, bottle_entity_mapper: BottleEntityMapper) -> None:
        self.bottle_entity_mapper = bottle_entity_mapper

    def to_entity(self, shelf: Shelf) -> ShelfEntity:
        return ShelfEntity(id=shelf.id, name=shelf.name, rows=shelf.rows, columns=shelf.columns)

    def to_domain(self, entity: ShelfEntity) -> Shelf:
        """Étagère seule : ne touche pas à entity.placements (pas de chargement des emplacements)."""
        return Shelf(id=entity.id, name=entity.name, rows=entity.rows, columns=entity.columns)

    def to_domain_with_placements(self, entity: ShelfEntity) -> Shelf:
        shelf = self.to_domain(entity)
        placements = sorted(entity.placements, key=lambda placement: (placement.row, placement.column))
        shelf.placements = [self._placement_to_domain(placement) for placement in placements]
        return shelf

    def _placement_to_domain(self, entity: BottlePlacementEntity) -> BottlePlacement:
        return BottlePlacement(
            id=entity.id,
            row=entity.row,
            column=entity.column,
            bottle=self.bottle_entity_mapper.to_domain(entity.bottle),
        )
