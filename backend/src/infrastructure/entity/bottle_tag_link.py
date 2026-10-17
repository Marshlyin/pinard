from uuid import UUID

from sqlmodel import Field, SQLModel


class BottleTagLink(SQLModel, table=True):
    """Table de liaison n-n entre bouteilles et étiquettes."""

    __tablename__ = "bottle_tag"

    bottle_id: UUID = Field(foreign_key="bottle.id", ondelete="CASCADE", primary_key=True)
    tag_id: UUID = Field(foreign_key="tag.id", ondelete="CASCADE", primary_key=True, index=True)
