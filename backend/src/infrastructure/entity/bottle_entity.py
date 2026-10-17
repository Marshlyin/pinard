from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from src.infrastructure.entity.bottle_tag_link import BottleTagLink

if TYPE_CHECKING:
    from src.infrastructure.entity.bottle_placement_entity import BottlePlacementEntity
    from src.infrastructure.entity.tag_entity import TagEntity


class BottleEntity(SQLModel, table=True):
    __tablename__ = "bottle"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    cuvee: str = Field(index=True)
    domain: str = Field(index=True)
    # Nullable pour les vins non millésimés (ex : champagne brut sans année)
    vintage: int | None = None

    placements: list["BottlePlacementEntity"] = Relationship(back_populates="bottle", cascade_delete=True)
    tags: list["TagEntity"] = Relationship(back_populates="bottles", link_model=BottleTagLink)

    @property
    def quantity(self) -> int:
        return len(self.placements)
