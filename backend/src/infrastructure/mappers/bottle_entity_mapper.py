from src.domain.model.bottle import Bottle
from src.infrastructure.entity.bottle_entity import BottleEntity


class BottleEntityMapper:
    """Bouteille seule, sans étiquettes ni emplacements (voir BottleDetailsEntityMapper)."""

    def to_entity(self, bottle: Bottle) -> BottleEntity:
        return BottleEntity(id=bottle.id, cuvee=bottle.cuvee, domain=bottle.domain, vintage=bottle.vintage)

    def to_domain(self, entity: BottleEntity) -> Bottle:
        return Bottle(id=entity.id, cuvee=entity.cuvee, domain=entity.domain, vintage=entity.vintage)
