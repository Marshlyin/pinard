from src.application.mappers import bottle_mapper, tag_category_mapper
from src.application.results.tag_result import TagDetailResult, TagResult
from src.domain.model.tag import Tag


def domain_to_result(tag: Tag) -> TagResult:
    return TagResult(
        id=tag.id, name=tag.name, color=tag.color, category=tag_category_mapper.domain_to_result(tag.category)
    )


def domain_to_detail_result(tag: Tag) -> TagDetailResult:
    return TagDetailResult(
        **domain_to_result(tag).model_dump(),
        bottles=[bottle_mapper.domain_to_summary_result(bottle) for bottle in tag.bottles],
    )
