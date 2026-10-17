from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.domain.model.bottle import Bottle
from src.domain.model.tag_category import TagCategory

# Gris neutre, utilisé quand aucune couleur n'est choisie à la création
DEFAULT_TAG_COLOR = "#9e9e9e"


@dataclass
class Tag:
    """Étiquette applicable librement aux bouteilles (ex : rouge, longue garde, fruité)."""

    name: str
    category: TagCategory
    color: str = DEFAULT_TAG_COLOR  # code hexadécimal #rrggbb, en minuscules
    id: UUID = field(default_factory=uuid4)
    # Renseigné uniquement quand l'étiquette est chargée en détail (voir TagRepository.find_by_id)
    bottles: list[Bottle] = field(default_factory=list)
