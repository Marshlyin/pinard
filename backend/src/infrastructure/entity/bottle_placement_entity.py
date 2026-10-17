from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.infrastructure.entity.bottle_entity import BottleEntity
    from src.infrastructure.entity.shelf_entity import ShelfEntity


class BottlePlacementEntity(SQLModel, table=True):
    """Une bouteille physique rangée dans une case d'une étagère (indices à partir de 1, rangée 1 en haut)."""

    __tablename__ = "bottle_placement"
    __table_args__ = (
        UniqueConstraint("shelf_id", "row", "column"),
        CheckConstraint('"row" >= 1', name="row_positive"),
        CheckConstraint('"column" >= 1', name="column_positive"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    bottle_id: UUID = Field(foreign_key="bottle.id", ondelete="CASCADE", index=True)
    shelf_id: UUID = Field(foreign_key="shelf.id", ondelete="RESTRICT")
    row: int
    column: int

    bottle: "BottleEntity" = Relationship(back_populates="placements")
    shelf: "ShelfEntity" = Relationship(back_populates="placements")
