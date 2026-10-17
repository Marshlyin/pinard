from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from src.domain.model.tag import DEFAULT_TAG_COLOR

# Code couleur hexadécimal #rrggbb, normalisé en minuscules
HexColor = Annotated[str, StringConstraints(pattern=r"^#[0-9a-fA-F]{6}$", to_lower=True)]


class CreateTagCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=50, description="Nom de l'étiquette", examples=["fruité"])
    category_id: UUID = Field(description="Identifiant de la catégorie de l'étiquette")
    color: HexColor = Field(
        default=DEFAULT_TAG_COLOR,
        description=f"Couleur d'affichage, au format #rrggbb (par défaut {DEFAULT_TAG_COLOR})",
        examples=["#8e1b3a"],
    )
