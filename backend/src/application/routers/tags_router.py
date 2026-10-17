from typing import Annotated
from uuid import UUID

from fastapi import Path, Query, status
from fastapi.routing import APIRouter

from src.application.commands.create_tag_command import CreateTagCommand
from src.application.commands.update_tag_command import UpdateTagCommand
from src.application.mappers import tag_mapper
from src.application.results.tag_result import TagDetailResult, TagResult
from src.configuration.injection_helper import injects
from src.configuration.logging import Logger
from src.domain.services.tags_service import TagsService
from src.transverse.application_constants import DEFAULT_RESPONSES

logger = Logger(child=True)

router = APIRouter(prefix="/tags", tags=["tags"], responses=DEFAULT_RESPONSES)

TagId = Annotated[UUID, Path(title="L'identifiant de l'étiquette")]


@router.post("", status_code=status.HTTP_201_CREATED, description="Create a new tag in a category")
def create_tag(
    command: CreateTagCommand,
    tags_service: TagsService = injects(TagsService),  # noqa: B008
) -> TagResult:
    logger.info("Début de l'appel au POST /tags")
    tag = tags_service.create_tag(command.name, command.category_id, command.color)
    logger.info("Fin de l'appel au POST /tags")
    return tag_mapper.domain_to_result(tag)


@router.get("", description="Get all the tags (minimal format), sorted by category then name")
def list_tags(
    category_id: Annotated[UUID | None, Query(description="Ne renvoie que les étiquettes de cette catégorie")] = None,
    tags_service: TagsService = injects(TagsService),  # noqa: B008
) -> list[TagResult]:
    logger.info("Début de l'appel au GET /tags")
    tags = tags_service.get_tags(category_id)
    logger.info("Fin de l'appel au GET /tags")
    return [tag_mapper.domain_to_result(tag) for tag in tags]


@router.get("/{id}", description="Get the detail of a tag, with the bottles it is applied to")
def get_tag(
    id: TagId,
    tags_service: TagsService = injects(TagsService),  # noqa: B008
) -> TagDetailResult:
    logger.info(f"Début de l'appel au GET /tags/{id}")
    tag = tags_service.get_tag(id)
    logger.info(f"Fin de l'appel au GET /tags/{id}")
    return tag_mapper.domain_to_detail_result(tag)


@router.put("/{id}", description="Update the name, the category and the color of a tag")
def update_tag(
    id: TagId,
    command: UpdateTagCommand,
    tags_service: TagsService = injects(TagsService),  # noqa: B008
) -> TagResult:
    logger.info(f"Début de l'appel au PUT /tags/{id}")
    tag = tags_service.update_tag(id, command.name, command.category_id, command.color)
    logger.info(f"Fin de l'appel au PUT /tags/{id}")
    return tag_mapper.domain_to_result(tag)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a tag and remove it from bottles")
def delete_tag(
    id: TagId,
    tags_service: TagsService = injects(TagsService),  # noqa: B008
) -> None:
    logger.info(f"Début de l'appel au DELETE /tags/{id}")
    tags_service.delete_tag(id)
    logger.info(f"Fin de l'appel au DELETE /tags/{id}")
