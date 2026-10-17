from uuid import UUID

from src.application.commands.create_bottle_command import CreateBottleCommand
from src.application.commands.update_bottle_command import UpdateBottleCommand
from src.application.mappers import tag_mapper
from src.application.results.bottle_result import (
    BottleDetailResult,
    BottleLocationResult,
    BottleResult,
    ShelfReferenceResult,
)
from src.application.results.bottle_summary_result import BottleSummaryResult
from src.domain.model.bottle import Bottle
from src.domain.model.bottle_location import BottleLocation


def command_to_domain(command: CreateBottleCommand) -> Bottle:
    return Bottle(cuvee=command.cuvee, domain=command.domain, vintage=command.vintage)


def update_command_to_domain(bottle_id: UUID, command: UpdateBottleCommand) -> Bottle:
    return Bottle(id=bottle_id, cuvee=command.cuvee, domain=command.domain, vintage=command.vintage)


def domain_to_summary_result(bottle: Bottle) -> BottleSummaryResult:
    return BottleSummaryResult(id=bottle.id, cuvee=bottle.cuvee, domain=bottle.domain, vintage=bottle.vintage)


def domain_to_result(bottle: Bottle) -> BottleResult:
    return BottleResult(
        **domain_to_summary_result(bottle).model_dump(),
        quantity=bottle.quantity,
        tags=[tag_mapper.domain_to_result(tag) for tag in bottle.tags],
    )


def domain_to_detail_result(bottle: Bottle) -> BottleDetailResult:
    return BottleDetailResult(
        **domain_to_result(bottle).model_dump(),
        placements=[location_to_result(location) for location in bottle.locations],
    )


def location_to_result(location: BottleLocation) -> BottleLocationResult:
    return BottleLocationResult(
        id=location.id,
        shelf=ShelfReferenceResult(id=location.shelf_id, name=location.shelf_name),
        row=location.row,
        column=location.column,
    )
