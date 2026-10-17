from uuid import UUID

from injector import inject

from src.configuration.logging import Logger
from src.domain.exceptions.domain_exceptions import BottleAlreadyExistsError, BottleNotFoundError, UnknownTagsError
from src.domain.model.bottle import Bottle
from src.domain.model.bottle_tag_filter import BottleTagFilter
from src.domain.model.tag import Tag
from src.domain.repositories.bottles_repository import BottleRepository
from src.domain.repositories.tags_repository import TagRepository

logger = Logger(child=True)


class BottlesService:
    @inject
    def __init__(self, bottle_repository: BottleRepository, tag_repository: TagRepository) -> None:
        self.bottle_repository = bottle_repository
        self.tag_repository = tag_repository

    def create_bottle(self, bottle: Bottle, tag_ids: list[UUID]) -> Bottle:
        self._check_is_not_duplicate(bottle)
        bottle.tags = self._get_existing_tags(tag_ids)

        created = self.bottle_repository.create(bottle)
        logger.info(f"Bouteille '{created.cuvee}' ({created.domain}, {created.vintage}) créée (id={created.id})")
        return created

    def update_bottle(self, bottle: Bottle, tag_ids: list[UUID]) -> Bottle:
        self.get_bottle(bottle.id)
        self._check_is_not_duplicate(bottle)
        bottle.tags = self._get_existing_tags(tag_ids)

        updated = self.bottle_repository.update(bottle)
        logger.info(f"Bouteille {updated.id} modifiée : '{updated.cuvee}' ({updated.domain}, {updated.vintage})")
        return updated

    def delete_bottle(self, bottle_id: UUID) -> None:
        bottle = self.get_bottle(bottle_id)

        self.bottle_repository.delete(bottle_id)
        logger.info(f"Bouteille {bottle_id} '{bottle.cuvee}' supprimée avec ses {bottle.quantity} emplacement(s)")

    def get_bottles(self, tag_ids: list[UUID] | None = None) -> list[Bottle]:
        """Toutes les bouteilles, ou celles qui correspondent aux étiquettes demandées (voir BottleTagFilter)."""
        if not tag_ids:
            return self.bottle_repository.find_all()

        unique_ids = list(dict.fromkeys(tag_ids))
        tags = self.tag_repository.find_by_ids(unique_ids)
        if len(tags) < len(unique_ids):
            # Étiquette inconnue : aucune bouteille ne peut la porter
            return []

        tag_filter = BottleTagFilter.from_tags(tags)
        return [bottle for bottle in self.bottle_repository.find_all() if tag_filter.matches(bottle)]

    def get_bottle(self, bottle_id: UUID) -> Bottle:
        bottle = self.bottle_repository.find_by_id(bottle_id)
        if bottle is None:
            raise BottleNotFoundError(bottle_id)
        return bottle

    def _check_is_not_duplicate(self, bottle: Bottle) -> None:
        """Triplet domaine + cuvée + millésime unique, la bouteille elle-même exceptée (cas d'une modification)."""
        for other in self.bottle_repository.find_all():
            if other.id != bottle.id and other.is_same_wine(bottle):
                raise BottleAlreadyExistsError(bottle.cuvee, bottle.domain, bottle.vintage)

    def _get_existing_tags(self, tag_ids: list[UUID]) -> list[Tag]:
        unique_ids = list(dict.fromkeys(tag_ids))  # dédoublonne en gardant l'ordre
        tags = self.tag_repository.find_by_ids(unique_ids)

        found_ids = {tag.id for tag in tags}
        missing_ids = [tag_id for tag_id in unique_ids if tag_id not in found_ids]
        if missing_ids:
            raise UnknownTagsError(missing_ids)
        return tags
