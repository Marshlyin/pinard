from sqlmodel import SQLModel

# Noms de contraintes stables : nécessaire au mode batch alembic sous SQLite pour pouvoir les modifier ou supprimer.
# Doit être défini avant l'import des entités.
SQLModel.metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Toutes les entités doivent être importées ici pour être enregistrées dans SQLModel.metadata (autogenerate alembic)
from src.infrastructure.entity.bottle_entity import BottleEntity  # noqa: E402
from src.infrastructure.entity.bottle_placement_entity import BottlePlacementEntity  # noqa: E402
from src.infrastructure.entity.bottle_tag_link import BottleTagLink  # noqa: E402
from src.infrastructure.entity.shelf_entity import ShelfEntity  # noqa: E402
from src.infrastructure.entity.tag_category_entity import TagCategoryEntity  # noqa: E402
from src.infrastructure.entity.tag_entity import TagEntity  # noqa: E402

__all__ = [
    "BottleEntity",
    "BottlePlacementEntity",
    "BottleTagLink",
    "ShelfEntity",
    "TagCategoryEntity",
    "TagEntity",
]
