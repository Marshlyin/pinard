from uuid import UUID

from injector import inject
from sqlalchemy import func
from sqlmodel import select

from src.domain.model.tag_category import TagCategory
from src.domain.repositories.tag_categories_repository import TagCategoryRepository
from src.infrastructure.dao.base_dao import BaseDAO
from src.infrastructure.entity.tag_category_entity import TagCategoryEntity
from src.infrastructure.entity.tag_entity import TagEntity
from src.infrastructure.mappers.tag_category_entity_mapper import TagCategoryEntityMapper


class TagCategoryRepositoryImpl(TagCategoryRepository):
    @inject
    def __init__(self, base_dao: BaseDAO, tag_category_entity_mapper: TagCategoryEntityMapper) -> None:
        self.base_dao = base_dao
        self.tag_category_entity_mapper = tag_category_entity_mapper

    def create(self, category: TagCategory) -> TagCategory:
        entity = self.tag_category_entity_mapper.to_entity(category)
        with self.base_dao.session() as session:
            session.add(entity)
            session.commit()
            return self.tag_category_entity_mapper.to_domain(entity)

    def update(self, category: TagCategory) -> TagCategory:
        with self.base_dao.session() as session:
            entity = session.get_one(TagCategoryEntity, category.id)
            entity.name = category.name
            session.commit()
            return self.tag_category_entity_mapper.to_domain(entity)

    def delete(self, category_id: UUID) -> None:
        with self.base_dao.session() as session:
            session.delete(session.get_one(TagCategoryEntity, category_id))
            session.commit()

    def find_all(self) -> list[TagCategory]:
        with self.base_dao.session() as session:
            entities = session.exec(select(TagCategoryEntity).order_by(TagCategoryEntity.name)).all()
            return [self.tag_category_entity_mapper.to_domain(entity) for entity in entities]

    def find_by_id(self, category_id: UUID) -> TagCategory | None:
        with self.base_dao.session() as session:
            entity = session.get(TagCategoryEntity, category_id)
            return self.tag_category_entity_mapper.to_domain(entity) if entity else None

    def count_tags(self, category_id: UUID) -> int:
        with self.base_dao.session() as session:
            return session.exec(
                select(func.count()).select_from(TagEntity).where(TagEntity.category_id == category_id)
            ).one()
