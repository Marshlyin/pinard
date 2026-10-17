from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.infrastructure.entity.bottle_placement_entity import BottlePlacementEntity


class ShelfEntity(SQLModel, table=True):
    __tablename__ = "shelf"
    __table_args__ = (
        CheckConstraint('"rows" >= 1', name="rows_positive"),
        CheckConstraint('"columns" >= 1', name="columns_positive"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True)
    rows: int
    columns: int

    # passive_deletes="all" : l'ORM ne touche pas aux emplacements, la base refuse la suppression (ON DELETE RESTRICT)
    placements: list["BottlePlacementEntity"] = Relationship(
        back_populates="shelf", sa_relationship_kwargs={"passive_deletes": "all"}
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.columns
