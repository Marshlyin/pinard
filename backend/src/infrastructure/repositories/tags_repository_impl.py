from uuid import UUID

from injector import inject
from sqlalchemy.orm import contains_eager, selectinload
from sqlmodel import select

from src.domain.model.tag import Tag
from src.domain.repositories.tags_repository import TagRepository
from src.infrastructure.dao.base_dao import BaseDAO
from src.infrastructure.entity.tag_category_entity import TagCategoryEntity
from src.infrastructure.entity.tag_entity import TagEntity
from src.infrastructure.mappers.tag_entity_mapper import TagEntityMapper


class TagRepositoryImpl(TagRepository):
    @inject
    def __init__(self, base_dao: BaseDAO, tag_entity_mapper: TagEntityMapper) -> None:
        self.base_dao = base_dao
        self.tag_entity_mapper = tag_entity_mapper

    def create(self, tag: Tag) -> Tag:
        entity = self.tag_entity_mapper.to_entity(tag)
        with self.base_dao.session() as session:
            session.add(entity)
            session.commit()
            # Charge la catégorie (relation non renseignée à la création, seul category_id l'est)
            session.refresh(entity)
            return self.tag_entity_mapper.to_domain(entity)

    def update(self, tag: Tag) -> Tag:
        with self.base_dao.session() as session:
            entity = session.get_one(TagEntity, tag.id)
            entity.name = tag.name
            entity.category_id = tag.category.id
            entity.color = tag.color
            session.commit()
            # Recharge la relation category, qui pointe encore vers l'ancienne catégorie en cas de changement
            session.refresh(entity)
            return self.tag_entity_mapper.to_domain(entity)

    def delete(self, tag_id: UUID) -> None:
        # Les lignes de bottle_tag sont supprimées par l'ORM (relation many-to-many) et par la base (ON DELETE CASCADE)
        with self.base_dao.session() as session:
            session.delete(session.get_one(TagEntity, tag_id))
            session.commit()

    def find_all(self, category_id: UUID | None = None) -> list[Tag]:
        statement = (
            select(TagEntity)
            .join(TagEntity.category)
            .options(contains_eager(TagEntity.category))
            .order_by(TagCategoryEntity.name, TagEntity.name)
        )
        if category_id is not None:
            statement = statement.where(TagEntity.category_id == category_id)

        with self.base_dao.session() as session:
            return [self.tag_entity_mapper.to_domain(entity) for entity in session.exec(statement).all()]

    def find_by_ids(self, tag_ids: list[UUID]) -> list[Tag]:
        if not tag_ids:
            return []
        statement = select(TagEntity).where(TagEntity.id.in_(tag_ids)).options(selectinload(TagEntity.category))
        with self.base_dao.session() as session:
            return [self.tag_entity_mapper.to_domain(entity) for entity in session.exec(statement).all()]

    def find_by_id(self, tag_id: UUID) -> Tag | None:
        statement = (
            select(TagEntity)
            .where(TagEntity.id == tag_id)
            .options(selectinload(TagEntity.category), selectinload(TagEntity.bottles))
        )
        with self.base_dao.session() as session:
            entity = session.exec(statement).first()
            return self.tag_entity_mapper.to_domain_with_bottles(entity) if entity else None
