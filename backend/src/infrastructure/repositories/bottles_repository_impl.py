from uuid import UUID

from injector import inject
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from src.domain.model.bottle import Bottle
from src.domain.model.tag import Tag
from src.domain.repositories.bottles_repository import BottleRepository
from src.infrastructure.dao.base_dao import BaseDAO
from src.infrastructure.entity.bottle_entity import BottleEntity
from src.infrastructure.entity.bottle_placement_entity import BottlePlacementEntity
from src.infrastructure.entity.tag_entity import TagEntity
from src.infrastructure.mappers.bottle_details_entity_mapper import BottleDetailsEntityMapper
from src.infrastructure.mappers.bottle_entity_mapper import BottleEntityMapper


class BottleRepositoryImpl(BottleRepository):
    @inject
    def __init__(
        self,
        base_dao: BaseDAO,
        bottle_entity_mapper: BottleEntityMapper,
        bottle_details_entity_mapper: BottleDetailsEntityMapper,
    ) -> None:
        self.base_dao = base_dao
        self.bottle_entity_mapper = bottle_entity_mapper
        self.bottle_details_entity_mapper = bottle_details_entity_mapper

    def create(self, bottle: Bottle) -> Bottle:
        entity = self.bottle_entity_mapper.to_entity(bottle)
        with self.base_dao.session() as session:
            entity.tags = self._load_tag_entities(session, bottle.tags)
            session.add(entity)
            session.commit()
            return self._find_by_id(session, bottle.id)

    def update(self, bottle: Bottle) -> Bottle:
        with self.base_dao.session() as session:
            entity = session.get_one(BottleEntity, bottle.id)
            entity.cuvee = bottle.cuvee
            entity.domain = bottle.domain
            entity.vintage = bottle.vintage
            entity.tags = self._load_tag_entities(session, bottle.tags)
            session.commit()
            return self._find_by_id(session, bottle.id)

    def delete(self, bottle_id: UUID) -> None:
        # Emplacements supprimés par l'ORM (cascade_delete) et par la base (ON DELETE CASCADE), de même que les liens
        # avec les étiquettes
        with self.base_dao.session() as session:
            session.delete(session.get_one(BottleEntity, bottle_id))
            session.commit()

    def find_all(self) -> list[Bottle]:
        with self.base_dao.session() as session:
            bottles = [self.bottle_details_entity_mapper.to_domain(e) for e in session.exec(self._select()).all()]
        return sorted(bottles, key=lambda bottle: bottle.sort_key)

    def find_by_id(self, bottle_id: UUID) -> Bottle | None:
        with self.base_dao.session() as session:
            entity = session.exec(self._select().where(BottleEntity.id == bottle_id)).first()
            return self.bottle_details_entity_mapper.to_domain(entity) if entity else None

    def _find_by_id(self, session: Session, bottle_id: UUID) -> Bottle:
        # populate_existing : l'entité est déjà dans la session, on force le rechargement de ses relations
        statement = self._select().where(BottleEntity.id == bottle_id).execution_options(populate_existing=True)
        return self.bottle_details_entity_mapper.to_domain(session.exec(statement).one())

    @staticmethod
    def _select() -> SelectOfScalar[BottleEntity]:
        # Étiquettes (avec catégorie) et emplacements (avec étagère) chargés en requêtes groupées (évite le N+1)
        return select(BottleEntity).options(
            selectinload(BottleEntity.tags).selectinload(TagEntity.category),
            selectinload(BottleEntity.placements).selectinload(BottlePlacementEntity.shelf),
        )

    @staticmethod
    def _load_tag_entities(session: Session, tags: list[Tag]) -> list[TagEntity]:
        if not tags:
            return []
        return list(session.exec(select(TagEntity).where(TagEntity.id.in_([tag.id for tag in tags]))).all())
