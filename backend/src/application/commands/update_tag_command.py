from pydantic import Field

from src.application.commands.create_tag_command import CreateTagCommand, HexColor


class UpdateTagCommand(CreateTagCommand):
    """Remplacement complet du nom, de la catégorie et de la couleur : mêmes contraintes qu'à la création."""

    # Obligatoire (contrairement à la création) : un oubli du champ ne doit pas remettre la couleur par défaut
    color: HexColor = Field(description="Couleur d'affichage, au format #rrggbb", examples=["#8e1b3a"])
