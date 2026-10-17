from uuid import UUID

from pydantic import BaseModel, Field

from src.application.results.tag_result import TagResult


class BottleResult(BaseModel):
    id: UUID
    cuvee: str
    domain: str
    vintage: int | None
    quantity: int = Field(description="Nombre de bouteilles physiques rangées dans les étagères")
    tags: list[TagResult] = Field(description="Étiquettes, triées par catégorie puis par nom")


class ShelfReferenceResult(BaseModel):
    id: UUID
    name: str


class BottleLocationResult(BaseModel):
    id: UUID = Field(description="Identifiant de l'emplacement (pour le déplacer ou le retirer)")
    shelf: ShelfReferenceResult
    row: int = Field(description="Rangée, à partir de 1 (1 = rangée du haut)")
    column: int = Field(description="Case dans la rangée, à partir de 1")


class BottleDetailResult(BottleResult):
    placements: list[BottleLocationResult] = Field(
        description="Emplacements des bouteilles physiques, triés par étagère, rangée puis case"
    )
