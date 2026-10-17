from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateBottleCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    cuvee: str = Field(min_length=1, max_length=100, description="Nom de la cuvée", examples=["Les Picasses"])
    domain: str = Field(min_length=1, max_length=100, description="Domaine producteur", examples=["Olga Raffault"])
    vintage: int | None = Field(
        default=None, ge=1800, le=2100, description="Millésime (absent pour un vin non millésimé)", examples=[2020]
    )
    tag_ids: list[UUID] = Field(default_factory=list, description="Étiquettes posées sur la bouteille")
