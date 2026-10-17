from uuid import UUID

from pydantic import BaseModel, Field

from src.application.results.bottle_summary_result import BottleSummaryResult
from src.application.results.tag_category_result import TagCategoryResult


class TagResult(BaseModel):
    """Format minimal d'une étiquette."""

    id: UUID
    name: str
    color: str = Field(description="Couleur d'affichage, au format #rrggbb")
    category: TagCategoryResult


class TagDetailResult(TagResult):
    bottles: list[BottleSummaryResult] = Field(
        description="Bouteilles portant l'étiquette, triées par domaine, cuvée puis millésime"
    )
