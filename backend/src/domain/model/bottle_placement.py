from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.domain.model.bottle import Bottle


@dataclass
class BottlePlacement:
    """
    Emplacement vu depuis l'étagère : la bouteille physique rangée dans une case (indices à partir de 1, rangée 1 en
    haut). (Vu depuis la bouteille, le même emplacement est un BottleLocation.)
    """

    row: int
    column: int
    bottle: Bottle
    id: UUID = field(default_factory=uuid4)
