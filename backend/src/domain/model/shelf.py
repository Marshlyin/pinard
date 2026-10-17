from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.domain.model.bottle_placement import BottlePlacement


@dataclass
class Shelf:
    """Étagère de rangement : une grille de rows × columns cases, une bouteille par case."""

    name: str
    rows: int
    columns: int
    id: UUID = field(default_factory=uuid4)
    # Renseigné uniquement quand l'étagère est chargée en détail (voir ShelfRepository.find_by_id)
    placements: list[BottlePlacement] = field(default_factory=list)

    @property
    def capacity(self) -> int:
        return self.rows * self.columns

    def has_slot(self, row: int, column: int) -> bool:
        return 1 <= row <= self.rows and 1 <= column <= self.columns

    def placement_at(self, row: int, column: int) -> BottlePlacement | None:
        """La bouteille rangée dans la case, si elle est occupée (nécessite les emplacements chargés)."""
        return next((p for p in self.placements if p.row == row and p.column == column), None)

    def placements_outside(self, rows: int, columns: int) -> list[BottlePlacement]:
        """Emplacements qui ne tiendraient plus dans une grille rows × columns."""
        return [placement for placement in self.placements if placement.row > rows or placement.column > columns]
