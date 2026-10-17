from uuid import UUID

from src.domain.exceptions.business_error_codes import BusinessErrorCode


class DomainError(Exception):
    """Violation d'une règle métier (renvoyée en 422 par l'application)."""

    def __init__(self, code: BusinessErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ResourceNotFoundError(DomainError):
    """Ressource demandée inexistante (renvoyée en 404 par l'application)."""


class ShelfNameAlreadyExistsError(DomainError):
    def __init__(self, name: str) -> None:
        super().__init__(BusinessErrorCode.SHELF_NAME_ALREADY_EXISTS, f"Une étagère nommée '{name}' existe déjà")


class ShelfTooSmallForPlacementsError(DomainError):
    def __init__(self, rows: int, columns: int, outside_count: int) -> None:
        super().__init__(
            BusinessErrorCode.SHELF_TOO_SMALL_FOR_PLACEMENTS,
            f"Impossible de passer l'étagère en {rows}x{columns} : "
            f"{outside_count} bouteille(s) se trouveraient hors de la grille",
        )


class ShelfNotEmptyError(DomainError):
    def __init__(self, name: str, bottle_count: int) -> None:
        super().__init__(
            BusinessErrorCode.SHELF_NOT_EMPTY,
            f"Impossible de supprimer l'étagère '{name}' : elle contient encore {bottle_count} bouteille(s)",
        )


class ShelfNotFoundError(ResourceNotFoundError):
    def __init__(self, shelf_id: UUID) -> None:
        super().__init__(BusinessErrorCode.SHELF_NOT_FOUND, f"Aucune étagère avec l'identifiant {shelf_id}")


class TagCategoryNameAlreadyExistsError(DomainError):
    def __init__(self, name: str) -> None:
        super().__init__(
            BusinessErrorCode.TAG_CATEGORY_NAME_ALREADY_EXISTS,
            f"Une catégorie d'étiquettes nommée '{name}' existe déjà",
        )


class TagCategoryNotEmptyError(DomainError):
    def __init__(self, name: str, tag_count: int) -> None:
        super().__init__(
            BusinessErrorCode.TAG_CATEGORY_NOT_EMPTY,
            f"Impossible de supprimer la catégorie '{name}' : elle contient encore {tag_count} étiquette(s)",
        )


class TagCategoryNotFoundError(ResourceNotFoundError):
    def __init__(self, category_id: UUID) -> None:
        super().__init__(
            BusinessErrorCode.TAG_CATEGORY_NOT_FOUND, f"Aucune catégorie d'étiquettes avec l'identifiant {category_id}"
        )


class UnknownTagCategoryError(DomainError):
    """Catégorie référencée dans le corps d'une requête sur une étiquette : 422 (et non 404, la ressource de l'URL
    n'est pas en cause)."""

    def __init__(self, category_id: UUID) -> None:
        super().__init__(
            BusinessErrorCode.UNKNOWN_TAG_CATEGORY, f"Aucune catégorie d'étiquettes avec l'identifiant {category_id}"
        )


class TagNameAlreadyExistsError(DomainError):
    def __init__(self, name: str, category_name: str) -> None:
        super().__init__(
            BusinessErrorCode.TAG_NAME_ALREADY_EXISTS,
            f"Une étiquette nommée '{name}' existe déjà dans la catégorie '{category_name}'",
        )


class TagNotFoundError(ResourceNotFoundError):
    def __init__(self, tag_id: UUID) -> None:
        super().__init__(BusinessErrorCode.TAG_NOT_FOUND, f"Aucune étiquette avec l'identifiant {tag_id}")


class UnknownTagsError(DomainError):
    """Étiquettes référencées dans le corps d'une requête sur une bouteille, mais inexistantes (422)."""

    def __init__(self, tag_ids: list[UUID]) -> None:
        super().__init__(
            BusinessErrorCode.UNKNOWN_TAGS, f"Étiquette(s) inexistante(s) : {', '.join(str(i) for i in tag_ids)}"
        )


class BottleAlreadyExistsError(DomainError):
    def __init__(self, cuvee: str, domain: str, vintage: int | None) -> None:
        super().__init__(
            BusinessErrorCode.BOTTLE_ALREADY_EXISTS,
            f"La bouteille '{cuvee}' du domaine '{domain}' ({vintage or 'sans millésime'}) existe déjà",
        )


class BottleNotFoundError(ResourceNotFoundError):
    def __init__(self, bottle_id: UUID) -> None:
        super().__init__(BusinessErrorCode.BOTTLE_NOT_FOUND, f"Aucune bouteille avec l'identifiant {bottle_id}")


class PlacementNotFoundError(ResourceNotFoundError):
    def __init__(self, bottle_id: UUID, placement_id: UUID) -> None:
        super().__init__(
            BusinessErrorCode.PLACEMENT_NOT_FOUND,
            f"Aucun emplacement {placement_id} pour la bouteille {bottle_id}",
        )


class UnknownShelfError(DomainError):
    """Étagère référencée dans le corps d'une requête sur un emplacement, mais inexistante (422)."""

    def __init__(self, shelf_id: UUID) -> None:
        super().__init__(BusinessErrorCode.UNKNOWN_SHELF, f"Aucune étagère avec l'identifiant {shelf_id}")


class SlotOutsideShelfError(DomainError):
    def __init__(self, shelf_name: str, rows: int, columns: int, row: int, column: int) -> None:
        super().__init__(
            BusinessErrorCode.SLOT_OUTSIDE_SHELF,
            f"La case (rangée {row}, case {column}) n'existe pas dans l'étagère '{shelf_name}' ({rows}x{columns})",
        )


class SlotAlreadyOccupiedError(DomainError):
    def __init__(self, shelf_name: str, row: int, column: int, cuvee: str, domain: str) -> None:
        super().__init__(
            BusinessErrorCode.SLOT_ALREADY_OCCUPIED,
            f"La case (rangée {row}, case {column}) de l'étagère '{shelf_name}' est déjà occupée "
            f"par '{cuvee}' du domaine '{domain}'",
        )
