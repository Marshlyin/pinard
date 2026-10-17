from src.domain.model.tag_category import TagCategory
from src.infrastructure.entity.tag_category_entity import TagCategoryEntity


class TagCategoryEntityMapper:
    def to_entity(self, category: TagCategory) -> TagCategoryEntity:
        return TagCategoryEntity(id=category.id, name=category.name)

    def to_domain(self, entity: TagCategoryEntity) -> TagCategory:
        return TagCategory(id=entity.id, name=entity.name)
