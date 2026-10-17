from uuid import UUID

from injector import inject

from src.configuration.logging import Logger
from src.domain.exceptions.domain_exceptions import (
    TagNameAlreadyExistsError,
    TagNotFoundError,
    UnknownTagCategoryError,
)
from src.domain.model.names import is_same_name
from src.domain.model.tag import Tag
from src.domain.model.tag_category import TagCategory
from src.domain.repositories.tag_categories_repository import TagCategoryRepository
from src.domain.repositories.tags_repository import TagRepository

logger = Logger(child=True)


class TagsService:
    @inject
    def __init__(self, tag_repository: TagRepository, tag_category_repository: TagCategoryRepository) -> None:
        self.tag_repository = tag_repository
        self.tag_category_repository = tag_category_repository

    def create_tag(self, name: str, category_id: UUID, color: str) -> Tag:
        tag = Tag(name=name, color=color, category=self._get_existing_category(category_id))
        self._check_name_is_free(tag)

        created = self.tag_repository.create(tag)
        logger.info(f"Étiquette '{created.name}' créée dans '{created.category.name}' (id={created.id})")
        return created

    def update_tag(self, tag_id: UUID, name: str, category_id: UUID, color: str) -> Tag:
        self.get_tag(tag_id)
        tag = Tag(id=tag_id, name=name, color=color, category=self._get_existing_category(category_id))
        self._check_name_is_free(tag)

        updated = self.tag_repository.update(tag)
        logger.info(f"Étiquette {updated.id} modifiée : '{updated.name}' dans '{updated.category.name}'")
        return updated

    def delete_tag(self, tag_id: UUID) -> None:
        tag = self.get_tag(tag_id)

        self.tag_repository.delete(tag_id)
        logger.info(f"Étiquette {tag_id} '{tag.name}' supprimée (retirée de {len(tag.bottles)} bouteille(s))")

    def get_tags(self, category_id: UUID | None = None) -> list[Tag]:
        return self.tag_repository.find_all(category_id)

    def get_tag(self, tag_id: UUID) -> Tag:
        tag = self.tag_repository.find_by_id(tag_id)
        if tag is None:
            raise TagNotFoundError(tag_id)
        return tag

    def _get_existing_category(self, category_id: UUID) -> TagCategory:
        category = self.tag_category_repository.find_by_id(category_id)
        if category is None:
            raise UnknownTagCategoryError(category_id)
        return category

    def _check_name_is_free(self, tag: Tag) -> None:
        """Nom unique dans sa catégorie sans tenir compte de la casse, l'étiquette elle-même exceptée (renommage)."""
        for other in self.tag_repository.find_all(tag.category.id):
            if other.id != tag.id and is_same_name(other.name, tag.name):
                raise TagNameAlreadyExistsError(tag.name, tag.category.name)
