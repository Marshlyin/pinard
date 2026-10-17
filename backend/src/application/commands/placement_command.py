from uuid import UUID

from pydantic import BaseModel, Field


class PlacementCommand(BaseModel):
    """Case cible pour ranger ou déplacer une bouteille physique."""

    shelf_id: UUID = Field(description="Identifiant de l'étagère")
    row: int = Field(ge=1, le=50, description="Rangée, à partir de 1 (1 = rangée du haut)", examples=[1])
    column: int = Field(ge=1, le=50, description="Case dans la rangée, à partir de 1", examples=[3])
