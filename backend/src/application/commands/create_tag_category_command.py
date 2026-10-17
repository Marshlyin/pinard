from pydantic import BaseModel, ConfigDict, Field


class CreateTagCategoryCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=50, description="Nom de la catégorie", examples=["Goût"])
