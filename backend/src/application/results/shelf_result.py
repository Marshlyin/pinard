from uuid import UUID

from pydantic import BaseModel, Field

from src.application.results.bottle_summary_result import BottleSummaryResult


class ShelfResult(BaseModel):
    """Format minimal d'une étagère."""

    id: UUID
    name: str
    rows: int
    columns: int
    capacity: int = Field(description="Nombre de bouteilles que l'étagère peut accueillir (rows × columns)")


class BottlePlacementResult(BaseModel):
    id: UUID = Field(description="Identifiant de l'emplacement (pour le déplacer ou le retirer)")
    row: int = Field(description="Rangée, à partir de 1 (1 = rangée du haut)")
    column: int = Field(description="Case dans la rangée, à partir de 1")
    bottle: BottleSummaryResult


class ShelfDetailResult(ShelfResult):
    placements: list[BottlePlacementResult] = Field(
        description="Emplacements occupés, triés par rangée puis case. Une bouteille peut y apparaître plusieurs fois"
    )
