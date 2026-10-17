from injector import inject

from src.domain.model.bottle import Bottle
from src.infrastructure.entity.bottle_entity import BottleEntity
from src.infrastructure.mappers.bottle_entity_mapper import BottleEntityMapper
from src.infrastructure.mappers.placement_entity_mapper import PlacementEntityMapper
from src.infrastructure.mappers.tag_entity_mapper import TagEntityMapper


class BottleDetailsEntityMapper:
    """
    Bouteille avec ses étiquettes et ses emplacements. Séparé de BottleEntityMapper pour éviter une dépendance
    circulaire : TagEntityMapper utilise BottleEntityMapper pour les bouteilles d'une étiquette.
    """

    @inject
    def __init__(
        self,
        bottle_entity_mapper: BottleEntityMapper,
        tag_entity_mapper: TagEntityMapper,
        placement_entity_mapper: PlacementEntityMapper,
    ) -> None:
        self.bottle_entity_mapper = bottle_entity_mapper
        self.tag_entity_mapper = tag_entity_mapper
        self.placement_entity_mapper = placement_entity_mapper

    def to_domain(self, entity: BottleEntity) -> Bottle:
        bottle = self.bottle_entity_mapper.to_domain(entity)
        bottle.tags = sorted(
            (self.tag_entity_mapper.to_domain(tag) for tag in entity.tags),
            key=lambda tag: (tag.category.name.casefold(), tag.name.casefold()),
        )
        bottle.locations = sorted(
            (self.placement_entity_mapper.to_location(placement) for placement in entity.placements),
            key=lambda location: (location.shelf_name.casefold(), location.row, location.column),
        )
        return bottle
