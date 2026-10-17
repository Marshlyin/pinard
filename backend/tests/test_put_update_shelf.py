from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.factories import create_bottle, create_shelf, place_bottle


def url(shelf_id: UUID | str) -> str:
    return f"/shelves/{shelf_id}"


def test_update_shelf_returns_200_with_new_values(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, name="Cave", rows=3, columns=4)

    response = client.put(url(shelf.id), json={"name": "Garage", "rows": 4, "columns": 5})

    assert response.status_code == 200
    assert response.json() == {"id": str(shelf.id), "name": "Garage", "rows": 4, "columns": 5, "capacity": 20}
    session.refresh(shelf)
    assert (shelf.name, shelf.rows, shelf.columns) == ("Garage", 4, 5)


def test_update_shelf_keeping_its_own_name_returns_200(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, name="Cave", rows=3, columns=4)

    response = client.put(url(shelf.id), json={"name": "Cave", "rows": 5, "columns": 5})

    assert response.status_code == 200
    assert response.json()["capacity"] == 25


def test_update_shelf_changing_only_case_returns_200(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, name="cave du bas")

    response = client.put(url(shelf.id), json={"name": "Cave du bas", "rows": 3, "columns": 4})

    assert response.status_code == 200
    assert response.json()["name"] == "Cave du bas"


def test_update_shelf_strips_name(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)

    response = client.put(url(shelf.id), json={"name": "  Garage  ", "rows": 3, "columns": 4})

    assert response.status_code == 200
    assert response.json()["name"] == "Garage"


@pytest.mark.parametrize("duplicate_name", ["Garage", "garage", "GARAGE"])
def test_update_shelf_with_name_of_another_shelf_returns_422(
    client: TestClient, session: Session, duplicate_name: str
) -> None:
    shelf = create_shelf(session, name="Cave")
    create_shelf(session, name="Garage")

    response = client.put(url(shelf.id), json={"name": duplicate_name, "rows": 3, "columns": 4})

    assert response.status_code == 422
    assert response.json() == {
        "code": "SHELF_NAME_ALREADY_EXISTS",
        "message": f"Une étagère nommée '{duplicate_name}' existe déjà",
    }
    session.refresh(shelf)
    assert shelf.name == "Cave"


@pytest.mark.parametrize(
    ("rows", "columns", "outside_count"),
    [
        (2, 4, 1),  # la rangée 3 disparaît
        (3, 3, 1),  # la case 4 disparaît
        (1, 1, 2),  # seule la case (1, 1) reste
    ],
)
def test_update_shelf_too_small_for_its_bottles_returns_422(
    client: TestClient, session: Session, rows: int, columns: int, outside_count: int
) -> None:
    shelf = create_shelf(session, rows=3, columns=4)
    bottle = create_bottle(session)
    place_bottle(session, bottle, shelf, row=1, column=1)
    place_bottle(session, bottle, shelf, row=3, column=1)
    place_bottle(session, bottle, shelf, row=1, column=4)

    response = client.put(url(shelf.id), json={"name": shelf.name, "rows": rows, "columns": columns})

    assert response.status_code == 422
    assert response.json() == {
        "code": "SHELF_TOO_SMALL_FOR_PLACEMENTS",
        "message": f"Impossible de passer l'étagère en {rows}x{columns} : "
        f"{outside_count} bouteille(s) se trouveraient hors de la grille",
    }
    session.refresh(shelf)
    assert (shelf.rows, shelf.columns) == (3, 4)


def test_update_shelf_shrinking_to_its_last_occupied_slot_returns_200(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, rows=4, columns=5)
    place_bottle(session, create_bottle(session), shelf, row=2, column=3)

    response = client.put(url(shelf.id), json={"name": shelf.name, "rows": 2, "columns": 3})

    assert response.status_code == 200
    assert response.json()["capacity"] == 6


def test_update_shelf_keeps_its_bottles(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, rows=3, columns=4)
    place_bottle(session, create_bottle(session), shelf, row=2, column=2)

    client.put(url(shelf.id), json={"name": "Garage", "rows": 6, "columns": 6})

    placements = client.get(url(shelf.id)).json()["placements"]
    assert [(p["row"], p["column"]) for p in placements] == [(2, 2)]


def test_update_unknown_shelf_returns_404(client: TestClient) -> None:
    unknown_id = uuid4()

    response = client.put(url(unknown_id), json={"name": "Cave", "rows": 3, "columns": 4})

    assert response.status_code == 404
    assert response.json()["code"] == "SHELF_NOT_FOUND"


def test_update_shelf_with_non_uuid_id_returns_400(client: TestClient) -> None:
    response = client.put(url("abc"), json={"name": "Cave", "rows": 3, "columns": 4})

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PARAMETERS"


@pytest.mark.parametrize(
    ("payload", "invalid_field"),
    [
        ({"name": "Cave", "rows": 0, "columns": 4}, "rows"),
        ({"name": "Cave", "rows": 3, "columns": 51}, "columns"),
        ({"name": "   ", "rows": 3, "columns": 4}, "name"),
        ({"name": "Cave", "rows": 3}, "columns"),
    ],
)
def test_update_shelf_with_invalid_parameters_returns_400(
    client: TestClient, session: Session, payload: dict, invalid_field: str
) -> None:
    shelf = create_shelf(session, name="Étagère", rows=3, columns=4)

    response = client.put(url(shelf.id), json=payload)

    assert response.status_code == 400
    assert [error["loc"] for error in response.json()["details"]] == [["body", invalid_field]]
    session.refresh(shelf)
    assert (shelf.name, shelf.rows, shelf.columns) == ("Étagère", 3, 4)
