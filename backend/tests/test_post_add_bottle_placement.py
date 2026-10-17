from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.infrastructure.entity import BottlePlacementEntity
from tests.factories import create_bottle, create_shelf, place_bottle


def url(bottle_id: UUID | str) -> str:
    return f"/bottles/{bottle_id}/placements"


def test_add_bottle_placement_returns_201(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, name="Cave", rows=3, columns=4)
    bottle = create_bottle(session)

    response = client.post(url(bottle.id), json={"shelf_id": str(shelf.id), "row": 2, "column": 3})

    assert response.status_code == 201
    body = response.json()
    assert body == {"id": body["id"], "shelf": {"id": str(shelf.id), "name": "Cave"}, "row": 2, "column": 3}
    placement = session.get(BottlePlacementEntity, UUID(body["id"]))
    assert placement is not None
    assert (placement.bottle_id, placement.shelf_id, placement.row, placement.column) == (bottle.id, shelf.id, 2, 3)


def test_add_bottle_placement_increases_quantity(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    bottle = create_bottle(session)

    client.post(url(bottle.id), json={"shelf_id": str(shelf.id), "row": 1, "column": 1})
    client.post(url(bottle.id), json={"shelf_id": str(shelf.id), "row": 1, "column": 2})

    assert client.get(f"/bottles/{bottle.id}").json()["quantity"] == 2
    assert len(client.get(f"/shelves/{shelf.id}").json()["placements"]) == 2


@pytest.mark.parametrize(("row", "column"), [(1, 1), (3, 4), (1, 4), (3, 1)])
def test_add_bottle_placement_in_grid_corners_returns_201(
    client: TestClient, session: Session, row: int, column: int
) -> None:
    shelf = create_shelf(session, rows=3, columns=4)

    response = client.post(
        url(create_bottle(session).id), json={"shelf_id": str(shelf.id), "row": row, "column": column}
    )

    assert response.status_code == 201


@pytest.mark.parametrize(("row", "column"), [(4, 1), (1, 5), (4, 5)])
def test_add_bottle_placement_outside_shelf_returns_422(
    client: TestClient, session: Session, row: int, column: int
) -> None:
    shelf = create_shelf(session, name="Cave", rows=3, columns=4)

    response = client.post(
        url(create_bottle(session).id), json={"shelf_id": str(shelf.id), "row": row, "column": column}
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "SLOT_OUTSIDE_SHELF",
        "message": f"La case (rangée {row}, case {column}) n'existe pas dans l'étagère 'Cave' (3x4)",
    }
    assert session.exec(select(BottlePlacementEntity)).all() == []


def test_add_bottle_placement_in_occupied_slot_returns_422(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, name="Cave")
    occupant = create_bottle(session, cuvee="Les Picasses", domain="Olga Raffault")
    place_bottle(session, occupant, shelf, row=1, column=2)
    bottle = create_bottle(session, cuvee="Autre", domain="Autre domaine")

    response = client.post(url(bottle.id), json={"shelf_id": str(shelf.id), "row": 1, "column": 2})

    assert response.status_code == 422
    assert response.json() == {
        "code": "SLOT_ALREADY_OCCUPIED",
        "message": "La case (rangée 1, case 2) de l'étagère 'Cave' est déjà occupée par 'Les Picasses' "
        "du domaine 'Olga Raffault'",
    }
    assert len(session.exec(select(BottlePlacementEntity)).all()) == 1


def test_add_bottle_placement_in_unknown_shelf_returns_422(client: TestClient, session: Session) -> None:
    unknown_id = uuid4()

    response = client.post(url(create_bottle(session).id), json={"shelf_id": str(unknown_id), "row": 1, "column": 1})

    assert response.status_code == 422
    assert response.json() == {"code": "UNKNOWN_SHELF", "message": f"Aucune étagère avec l'identifiant {unknown_id}"}


def test_add_placement_to_unknown_bottle_returns_404(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)

    response = client.post(url(uuid4()), json={"shelf_id": str(shelf.id), "row": 1, "column": 1})

    assert response.status_code == 404
    assert response.json()["code"] == "BOTTLE_NOT_FOUND"


@pytest.mark.parametrize(
    ("body", "invalid_field"),
    [
        ({"row": 1, "column": 1}, "shelf_id"),
        ({"shelf_id": "abc", "row": 1, "column": 1}, "shelf_id"),
        ({"shelf_id": "00000000-0000-4000-8000-000000000000", "row": 0, "column": 1}, "row"),
        ({"shelf_id": "00000000-0000-4000-8000-000000000000", "row": 1, "column": 0}, "column"),
        ({"shelf_id": "00000000-0000-4000-8000-000000000000", "row": 1}, "column"),
    ],
)
def test_add_bottle_placement_with_invalid_parameters_returns_400(
    client: TestClient, session: Session, body: dict, invalid_field: str
) -> None:
    response = client.post(url(create_bottle(session).id), json=body)

    assert response.status_code == 400
    assert [error["loc"] for error in response.json()["details"]] == [["body", invalid_field]]


def test_add_bottle_placement_with_non_uuid_bottle_id_returns_400(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)

    response = client.post(url("abc"), json={"shelf_id": str(shelf.id), "row": 1, "column": 1})

    assert response.status_code == 400
