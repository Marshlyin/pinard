from src.domain.model.bottle_location import BottleLocation
from src.infrastructure.entity.bottle_placement_entity import BottlePlacementEntity


class PlacementEntityMapper:
    def to_entity(self, location: BottleLocation) -> BottlePlacementEntity:
        return BottlePlacementEntity(
            id=location.id,
            bottle_id=location.bottle_id,
            shelf_id=location.shelf_id,
            row=location.row,
            column=location.column,
        )

    def to_location(self, entity: BottlePlacementEntity) -> BottleLocation:
        """Nécessite entity.shelf (chargé ou chargeable dans la session) pour le nom de l'étagère."""
        return BottleLocation(
            id=entity.id,
            bottle_id=entity.bottle_id,
            shelf_id=entity.shelf_id,
            shelf_name=entity.shelf.name,
            row=entity.row,
            column=entity.column,
        )
