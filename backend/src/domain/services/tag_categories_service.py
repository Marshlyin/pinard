from uuid import UUID

from injector import inject

from src.configuration.logging import Logger
from src.domain.exceptions.domain_exceptions import (
    TagCategoryNameAlreadyExistsError,
    TagCategoryNotEmptyError,
    TagCategoryNotFoundError,
)
from src.domain.model.names import is_same_name
from src.domain.model.tag_category import TagCategory
from src.domain.repositories.tag_categories_repository import TagCategoryRepository

logger = Logger(child=True)


class TagCategoriesService:
    @inject
    def __init__(self, tag_category_repository: TagCategoryRepository) -> None:
        self.tag_category_repository = tag_category_repository

    def create_category(self, category: TagCategory) -> TagCategory:
        self._check_name_is_free(category)

        created = self.tag_category_repository.create(category)
        logger.info(f"Catégorie d'étiquettes '{created.name}' créée (id={created.id})")
        return created

    def update_category(self, category: TagCategory) -> TagCategory:
        self.get_category(category.id)
        self._check_name_is_free(category)

        updated = self.tag_category_repository.update(category)
        logger.info(f"Catégorie d'étiquettes {updated.id} renommée en '{updated.name}'")
        return updated

    def delete_category(self, category_id: UUID) -> None:
        category = self.get_category(category_id)

        tag_count = self.tag_category_repository.count_tags(category_id)
        if tag_count:
            raise TagCategoryNotEmptyError(category.name, tag_count)

        self.tag_category_repository.delete(category_id)
        logger.info(f"Catégorie d'étiquettes {category_id} '{category.name}' supprimée")

    def get_categories(self) -> list[TagCategory]:
        return self.tag_category_repository.find_all()

    def get_category(self, category_id: UUID) -> TagCategory:
        category = self.tag_category_repository.find_by_id(category_id)
        if category is None:
            raise TagCategoryNotFoundError(category_id)
        return category

    def _check_name_is_free(self, category: TagCategory) -> None:
        """Nom unique sans tenir compte de la casse, la catégorie elle-même exceptée (cas d'un renommage)."""
        for other in self.tag_category_repository.find_all():
            if other.id != category.id and is_same_name(other.name, category.name):
                raise TagCategoryNameAlreadyExistsError(category.name)
