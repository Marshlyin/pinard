from typing import Annotated
from uuid import UUID

from fastapi import Path, status
from fastapi.routing import APIRouter

from src.application.commands.create_tag_category_command import CreateTagCategoryCommand
from src.application.commands.update_tag_category_command import UpdateTagCategoryCommand
from src.application.mappers import tag_category_mapper
from src.application.results.tag_category_result import TagCategoryResult
from src.configuration.injection_helper import injects
from src.configuration.logging import Logger
from src.domain.services.tag_categories_service import TagCategoriesService
from src.transverse.application_constants import DEFAULT_RESPONSES

logger = Logger(child=True)

router = APIRouter(prefix="/tag-categories", tags=["tag-categories"], responses=DEFAULT_RESPONSES)

CategoryId = Annotated[UUID, Path(title="L'identifiant de la catégorie d'étiquettes")]


@router.post("", status_code=status.HTTP_201_CREATED, description="Create a new tag category")
def create_tag_category(
    command: CreateTagCategoryCommand,
    tag_categories_service: TagCategoriesService = injects(TagCategoriesService),  # noqa: B008
) -> TagCategoryResult:
    logger.info("Début de l'appel au POST /tag-categories")
    category = tag_categories_service.create_category(tag_category_mapper.command_to_domain(command))
    logger.info("Fin de l'appel au POST /tag-categories")
    return tag_category_mapper.domain_to_result(category)


@router.get("", description="Get all the tag categories, sorted by name")
def list_tag_categories(
    tag_categories_service: TagCategoriesService = injects(TagCategoriesService),  # noqa: B008
) -> list[TagCategoryResult]:
    logger.info("Début de l'appel au GET /tag-categories")
    categories = tag_categories_service.get_categories()
    logger.info("Fin de l'appel au GET /tag-categories")
    return [tag_category_mapper.domain_to_result(category) for category in categories]


@router.get("/{id}", description="Get a tag category")
def get_tag_category(
    id: CategoryId,
    tag_categories_service: TagCategoriesService = injects(TagCategoriesService),  # noqa: B008
) -> TagCategoryResult:
    logger.info(f"Début de l'appel au GET /tag-categories/{id}")
    category = tag_categories_service.get_category(id)
    logger.info(f"Fin de l'appel au GET /tag-categories/{id}")
    return tag_category_mapper.domain_to_result(category)


@router.put("/{id}", description="Rename a tag category")
def update_tag_category(
    id: CategoryId,
    command: UpdateTagCategoryCommand,
    tag_categories_service: TagCategoriesService = injects(TagCategoriesService),  # noqa: B008
) -> TagCategoryResult:
    logger.info(f"Début de l'appel au PUT /tag-categories/{id}")
    category = tag_categories_service.update_category(tag_category_mapper.update_command_to_domain(id, command))
    logger.info(f"Fin de l'appel au PUT /tag-categories/{id}")
    return tag_category_mapper.domain_to_result(category)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a tag category without tags")
def delete_tag_category(
    id: CategoryId,
    tag_categories_service: TagCategoriesService = injects(TagCategoriesService),  # noqa: B008
) -> None:
    logger.info(f"Début de l'appel au DELETE /tag-categories/{id}")
    tag_categories_service.delete_category(id)
    logger.info(f"Fin de l'appel au DELETE /tag-categories/{id}")
