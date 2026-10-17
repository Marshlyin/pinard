from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from src.domain.model.names import is_same_name

if TYPE_CHECKING:
    from src.domain.model.bottle_location import BottleLocation
    from src.domain.model.tag import Tag


@dataclass
class Bottle:
    """Référence de vin. Peut correspondre à plusieurs bouteilles physiques (une par emplacement)."""

    cuvee: str
    domain: str
    vintage: int | None = None
    id: UUID = field(default_factory=uuid4)
    # Renseignés quand la bouteille est chargée par BottleRepository (vides dans le détail d'une étagère ou d'une
    # étiquette, qui n'en ont pas besoin)
    tags: list[Tag] = field(default_factory=list)
    locations: list[BottleLocation] = field(default_factory=list)

    @property
    def quantity(self) -> int:
        """Nombre de bouteilles physiques rangées."""
        return len(self.locations)

    @property
    def sort_key(self) -> tuple[str, str, int]:
        """Ordre d'affichage : domaine, cuvée puis millésime (sans tenir compte de la casse)."""
        return self.domain.casefold(), self.cuvee.casefold(), self.vintage or 0

    def is_same_wine(self, other: Bottle) -> bool:
        """Même domaine, même cuvée (sans tenir compte de la casse) et même millésime."""
        return (
            is_same_name(self.domain, other.domain)
            and is_same_name(self.cuvee, other.cuvee)
            and self.vintage == other.vintage
        )
