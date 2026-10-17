from pydantic import BaseModel, ConfigDict, Field


class CreateShelfCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100, description="Nom de l'étagère", examples=["Étagère du haut"])
    rows: int = Field(ge=1, le=50, description="Nombre de rangées", examples=[4])
    columns: int = Field(ge=1, le=50, description="Nombre de cases par rangée", examples=[5])
