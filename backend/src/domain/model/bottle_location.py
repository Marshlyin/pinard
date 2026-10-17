from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class BottleLocation:
    """
    Emplacement vu depuis la bouteille : où se trouve un de ses exemplaires physiques.
    (Vu depuis l'étagère, le même emplacement est un BottlePlacement.)
    """

    bottle_id: UUID
    shelf_id: UUID
    shelf_name: str
    row: int
    column: int
    id: UUID = field(default_factory=uuid4)
