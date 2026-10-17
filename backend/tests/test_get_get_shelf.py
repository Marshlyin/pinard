from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.factories import create_bottle, create_shelf, place_bottle


def url(shelf_id: UUID | str) -> str:
    return f"/shelves/{shelf_id}"


def test_get_shelf_without_bottle_returns_empty_placements(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, name="Cave", rows=4, columns=5)

    response = client.get(url(shelf.id))

    assert response.status_code == 200
    assert response.json() == {
        "id": str(shelf.id),
        "name": "Cave",
        "rows": 4,
        "columns": 5,
        "capacity": 20,
        "placements": [],
    }


def test_get_shelf_returns_bottles_sorted_by_row_then_column(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    chinon = create_bottle(session, cuvee="Les Picasses", domain="Olga Raffault", vintage=2020)
    champagne = create_bottle(session, cuvee="Brut Réserve", domain="Billecart-Salmon", vintage=None)
    # Une même bouteille sur 2 cases, insérées dans le désordre
    chinon_2_1 = place_bottle(session, chinon, shelf, row=2, column=1)
    champagne_1_3 = place_bottle(session, champagne, shelf, row=1, column=3)
    chinon_1_1 = place_bottle(session, chinon, shelf, row=1, column=1)

    response = client.get(url(shelf.id))

    assert response.status_code == 200
    chinon_json = {"id": str(chinon.id), "cuvee": "Les Picasses", "domain": "Olga Raffault", "vintage": 2020}
    champagne_json = {"id": str(champagne.id), "cuvee": "Brut Réserve", "domain": "Billecart-Salmon", "vintage": None}
    assert response.json()["placements"] == [
        {"id": str(chinon_1_1.id), "row": 1, "column": 1, "bottle": chinon_json},
        {"id": str(champagne_1_3.id), "row": 1, "column": 3, "bottle": champagne_json},
        {"id": str(chinon_2_1.id), "row": 2, "column": 1, "bottle": chinon_json},
    ]


def test_get_shelf_returns_only_its_own_bottles(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, name="Cave")
    other_shelf = create_shelf(session, name="Garage")
    bottle = create_bottle(session)
    place_bottle(session, bottle, shelf, row=1, column=1)
    place_bottle(session, bottle, other_shelf, row=2, column=2)

    response = client.get(url(shelf.id))

    assert response.status_code == 200
    assert [(p["row"], p["column"]) for p in response.json()["placements"]] == [(1, 1)]


def test_get_unknown_shelf_returns_404(client: TestClient, session: Session) -> None:
    create_shelf(session)
    unknown_id = uuid4()

    response = client.get(url(unknown_id))

    assert response.status_code == 404
    assert response.json() == {"code": "SHELF_NOT_FOUND", "message": f"Aucune étagère avec l'identifiant {unknown_id}"}


@pytest.mark.parametrize("invalid_id", ["abc", "42", "123e4567-e89b-12d3-a456"])
def test_get_shelf_with_non_uuid_id_returns_400(client: TestClient, invalid_id: str) -> None:
    response = client.get(url(invalid_id))

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PARAMETERS"
