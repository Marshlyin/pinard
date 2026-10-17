from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.infrastructure.entity.tag_entity import TagEntity


class TagCategoryEntity(SQLModel, table=True):
    __tablename__ = "tag_category"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True)

    # passive_deletes="all" : l'ORM ne touche pas aux étiquettes, la base refuse la suppression (ON DELETE RESTRICT)
    tags: list["TagEntity"] = Relationship(back_populates="category", sa_relationship_kwargs={"passive_deletes": "all"})
