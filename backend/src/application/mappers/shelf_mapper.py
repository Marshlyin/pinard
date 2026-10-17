from uuid import UUID

from src.application.commands.create_shelf_command import CreateShelfCommand
from src.application.commands.update_shelf_command import UpdateShelfCommand
from src.application.mappers import bottle_mapper
from src.application.results.shelf_result import BottlePlacementResult, ShelfDetailResult, ShelfResult
from src.domain.model.shelf import Shelf


def command_to_domain(command: CreateShelfCommand) -> Shelf:
    return Shelf(name=command.name, rows=command.rows, columns=command.columns)


def update_command_to_domain(shelf_id: UUID, command: UpdateShelfCommand) -> Shelf:
    return Shelf(id=shelf_id, name=command.name, rows=command.rows, columns=command.columns)


def domain_to_result(shelf: Shelf) -> ShelfResult:
    return ShelfResult(id=shelf.id, name=shelf.name, rows=shelf.rows, columns=shelf.columns, capacity=shelf.capacity)


def domain_to_detail_result(shelf: Shelf) -> ShelfDetailResult:
    return ShelfDetailResult(
        **domain_to_result(shelf).model_dump(),
        placements=[
            BottlePlacementResult(
                id=placement.id,
                row=placement.row,
                column=placement.column,
                bottle=bottle_mapper.domain_to_summary_result(placement.bottle),
            )
            for placement in shelf.placements
        ],
    )
