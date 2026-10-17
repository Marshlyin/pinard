from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class TagCategory:
    """Catégorie d'étiquettes créée par l'utilisateur (ex : Type, Garde, Goût, Odeur)."""

    name: str
    id: UUID = field(default_factory=uuid4)
