"""Insertion directe en base des données de test."""

from sqlmodel import Session

from src.domain.model.tag import DEFAULT_TAG_COLOR
from src.infrastructure.entity import (
    BottleEntity,
    BottlePlacementEntity,
    BottleTagLink,
    ShelfEntity,
    TagCategoryEntity,
    TagEntity,
)


def create_shelf(session: Session, name: str = "Étagère", rows: int = 3, columns: int = 4) -> ShelfEntity:
    shelf = ShelfEntity(name=name, rows=rows, columns=columns)
    session.add(shelf)
    session.commit()
    session.refresh(shelf)
    return shelf


def create_bottle(
    session: Session, cuvee: str = "Les Picasses", domain: str = "Olga Raffault", vintage: int | None = 2020
) -> BottleEntity:
    bottle = BottleEntity(cuvee=cuvee, domain=domain, vintage=vintage)
    session.add(bottle)
    session.commit()
    session.refresh(bottle)
    return bottle


def place_bottle(
    session: Session, bottle: BottleEntity, shelf: ShelfEntity, row: int, column: int
) -> BottlePlacementEntity:
    placement = BottlePlacementEntity(bottle_id=bottle.id, shelf_id=shelf.id, row=row, column=column)
    session.add(placement)
    session.commit()
    session.refresh(placement)
    return placement


def create_tag_category(session: Session, name: str = "Goût") -> TagCategoryEntity:
    category = TagCategoryEntity(name=name)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def create_tag(
    session: Session, category: TagCategoryEntity, name: str = "fruité", color: str = DEFAULT_TAG_COLOR
) -> TagEntity:
    tag = TagEntity(name=name, category_id=category.id, color=color)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


def tag_bottle(session: Session, bottle: BottleEntity, tag: TagEntity) -> None:
    session.add(BottleTagLink(bottle_id=bottle.id, tag_id=tag.id))
    session.commit()
