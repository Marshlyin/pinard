from uuid import UUID

from injector import inject
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.domain.model.shelf import Shelf
from src.domain.repositories.shelves_repository import ShelfRepository
from src.infrastructure.dao.base_dao import BaseDAO
from src.infrastructure.entity.bottle_placement_entity import BottlePlacementEntity
from src.infrastructure.entity.shelf_entity import ShelfEntity
from src.infrastructure.mappers.shelf_entity_mapper import ShelfEntityMapper


class ShelfRepositoryImpl(ShelfRepository):
    @inject
    def __init__(self, base_dao: BaseDAO, shelf_entity_mapper: ShelfEntityMapper) -> None:
        self.base_dao = base_dao
        self.shelf_entity_mapper = shelf_entity_mapper

    def create(self, shelf: Shelf) -> Shelf:
        entity = self.shelf_entity_mapper.to_entity(shelf)
        with self.base_dao.session() as session:
            session.add(entity)
            session.commit()
            return self.shelf_entity_mapper.to_domain(entity)

    def update(self, shelf: Shelf) -> Shelf:
        with self.base_dao.session() as session:
            entity = session.get_one(ShelfEntity, shelf.id)
            entity.name = shelf.name
            entity.rows = shelf.rows
            entity.columns = shelf.columns
            session.commit()
            return self.shelf_entity_mapper.to_domain(entity)

    def delete(self, shelf_id: UUID) -> None:
        with self.base_dao.session() as session:
            session.delete(session.get_one(ShelfEntity, shelf_id))
            session.commit()

    def find_all(self) -> list[Shelf]:
        with self.base_dao.session() as session:
            entities = session.exec(select(ShelfEntity).order_by(ShelfEntity.name)).all()
            return [self.shelf_entity_mapper.to_domain(entity) for entity in entities]

    def find_by_id(self, shelf_id: UUID) -> Shelf | None:
        # Chargement des emplacements et de leurs bouteilles en 2 requêtes groupées (évite le N+1)
        statement = (
            select(ShelfEntity)
            .where(ShelfEntity.id == shelf_id)
            .options(selectinload(ShelfEntity.placements).selectinload(BottlePlacementEntity.bottle))
        )
        with self.base_dao.session() as session:
            entity = session.exec(statement).first()
            return self.shelf_entity_mapper.to_domain_with_placements(entity) if entity else None
