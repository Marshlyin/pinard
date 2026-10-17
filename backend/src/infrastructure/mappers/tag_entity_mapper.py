from injector import inject

from src.domain.model.tag import Tag
from src.infrastructure.entity.tag_entity import TagEntity
from src.infrastructure.mappers.bottle_entity_mapper import BottleEntityMapper
from src.infrastructure.mappers.tag_category_entity_mapper import TagCategoryEntityMapper


class TagEntityMapper:
    @inject
    def __init__(
        self, tag_category_entity_mapper: TagCategoryEntityMapper, bottle_entity_mapper: BottleEntityMapper
    ) -> None:
        self.tag_category_entity_mapper = tag_category_entity_mapper
        self.bottle_entity_mapper = bottle_entity_mapper

    def to_entity(self, tag: Tag) -> TagEntity:
        return TagEntity(id=tag.id, name=tag.name, category_id=tag.category.id, color=tag.color)

    def to_domain(self, entity: TagEntity) -> Tag:
        """Étiquette avec sa catégorie : ne touche pas à entity.bottles (pas de chargement des bouteilles)."""
        return Tag(
            id=entity.id,
            name=entity.name,
            color=entity.color,
            category=self.tag_category_entity_mapper.to_domain(entity.category),
        )

    def to_domain_with_bottles(self, entity: TagEntity) -> Tag:
        tag = self.to_domain(entity)
        tag.bottles = sorted(
            (self.bottle_entity_mapper.to_domain(bottle) for bottle in entity.bottles), key=lambda b: b.sort_key
        )
        return tag
