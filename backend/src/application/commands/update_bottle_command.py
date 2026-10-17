from uuid import UUID

from pydantic import Field

from src.application.commands.create_bottle_command import CreateBottleCommand


class UpdateBottleCommand(CreateBottleCommand):
    """Remplacement complet de la bouteille, étiquettes comprises. Les emplacements ne sont pas modifiés."""

    # Obligatoire (contrairement à la création) : un oubli du champ ne doit pas retirer toutes les étiquettes
    tag_ids: list[UUID] = Field(description="Liste complète des étiquettes (remplace la liste actuelle)")
