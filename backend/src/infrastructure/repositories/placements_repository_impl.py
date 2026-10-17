from uuid import UUID

from injector import inject

from src.domain.model.bottle_location import BottleLocation
from src.domain.repositories.placements_repository import PlacementRepository
from src.infrastructure.dao.base_dao import BaseDAO
from src.infrastructure.entity.bottle_placement_entity import BottlePlacementEntity
from src.infrastructure.mappers.placement_entity_mapper import PlacementEntityMapper


class PlacementRepositoryImpl(PlacementRepository):
    @inject
    def __init__(self, base_dao: BaseDAO, placement_entity_mapper: PlacementEntityMapper) -> None:
        self.base_dao = base_dao
        self.placement_entity_mapper = placement_entity_mapper

    def create(self, location: BottleLocation) -> BottleLocation:
        entity = self.placement_entity_mapper.to_entity(location)
        with self.base_dao.session() as session:
            session.add(entity)
            session.commit()
            session.refresh(entity)  # charge la relation shelf (seul shelf_id est renseigné à la création)
            return self.placement_entity_mapper.to_location(entity)

    def update(self, location: BottleLocation) -> BottleLocation:
        with self.base_dao.session() as session:
            entity = session.get_one(BottlePlacementEntity, location.id)
            entity.shelf_id = location.shelf_id
            entity.row = location.row
            entity.column = location.column
            session.commit()
            session.refresh(entity)  # recharge la relation shelf, qui pointe encore vers l'ancienne étagère
            return self.placement_entity_mapper.to_location(entity)

    def delete(self, placement_id: UUID) -> None:
        with self.base_dao.session() as session:
            session.delete(session.get_one(BottlePlacementEntity, placement_id))
            session.commit()

    def find_by_id(self, placement_id: UUID) -> BottleLocation | None:
        with self.base_dao.session() as session:
            entity = session.get(BottlePlacementEntity, placement_id)
            return self.placement_entity_mapper.to_location(entity) if entity else None
