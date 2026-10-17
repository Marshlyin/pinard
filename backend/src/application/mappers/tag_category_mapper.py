from uuid import UUID

from src.application.commands.create_tag_category_command import CreateTagCategoryCommand
from src.application.commands.update_tag_category_command import UpdateTagCategoryCommand
from src.application.results.tag_category_result import TagCategoryResult
from src.domain.model.tag_category import TagCategory


def command_to_domain(command: CreateTagCategoryCommand) -> TagCategory:
    return TagCategory(name=command.name)


def update_command_to_domain(category_id: UUID, command: UpdateTagCategoryCommand) -> TagCategory:
    return TagCategory(id=category_id, name=command.name)


def domain_to_result(category: TagCategory) -> TagCategoryResult:
    return TagCategoryResult(id=category.id, name=category.name)
