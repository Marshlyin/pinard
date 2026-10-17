from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.factories import create_bottle, create_shelf, place_bottle

URL = "/shelves"


def test_list_shelves_without_shelf_returns_empty_list(client: TestClient) -> None:
    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() == []


def test_list_shelves_returns_minimal_format_sorted_by_name(client: TestClient, session: Session) -> None:
    cellar = create_shelf(session, name="Cave", rows=4, columns=5)
    bottom = create_shelf(session, name="Bas", rows=3, columns=4)

    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() == [
        {"id": str(bottom.id), "name": "Bas", "rows": 3, "columns": 4, "capacity": 12},
        {"id": str(cellar.id), "name": "Cave", "rows": 4, "columns": 5, "capacity": 20},
    ]


def test_list_shelves_does_not_return_placements(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    place_bottle(session, create_bottle(session), shelf, row=1, column=1)

    response = client.get(URL)

    assert response.status_code == 200
    assert "placements" not in response.json()[0]
