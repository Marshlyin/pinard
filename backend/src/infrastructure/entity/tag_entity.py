from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from src.infrastructure.entity.bottle_tag_link import BottleTagLink

if TYPE_CHECKING:
    from src.infrastructure.entity.bottle_entity import BottleEntity
    from src.infrastructure.entity.tag_category_entity import TagCategoryEntity


class TagEntity(SQLModel, table=True):
    __tablename__ = "tag"
    # Un même nom peut exister dans deux catégories (ex : « fruité » en Goût et en Odeur)
    __table_args__ = (UniqueConstraint("category_id", "name"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    category_id: UUID = Field(foreign_key="tag_category.id", ondelete="RESTRICT", index=True)
    color: str = Field(max_length=7)  # code hexadécimal #rrggbb

    category: "TagCategoryEntity" = Relationship(back_populates="tags")
    bottles: list["BottleEntity"] = Relationship(back_populates="tags", link_model=BottleTagLink)
