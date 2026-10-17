from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

from src.domain.model.bottle import Bottle
from src.domain.model.tag import Tag


@dataclass
class BottleTagFilter:
    """
    Filtre des bouteilles par étiquettes : OU entre les étiquettes d'une même catégorie, ET entre les catégories.
    Ex : rouge, blanc (Type) et longue garde (Garde) → (rouge OU blanc) ET longue garde.
    """

    tag_ids_by_category: dict[UUID, set[UUID]]

    @classmethod
    def from_tags(cls, tags: list[Tag]) -> "BottleTagFilter":
        tag_ids_by_category: dict[UUID, set[UUID]] = defaultdict(set)
        for tag in tags:
            tag_ids_by_category[tag.category.id].add(tag.id)
        return cls(dict(tag_ids_by_category))

    def matches(self, bottle: Bottle) -> bool:
        """La bouteille porte au moins une des étiquettes demandées dans chaque catégorie."""
        bottle_tag_ids = {tag.id for tag in bottle.tags}
        return all(tag_ids & bottle_tag_ids for tag_ids in self.tag_ids_by_category.values())
