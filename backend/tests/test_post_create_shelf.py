from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.infrastructure.entity import ShelfEntity

URL = "/shelves"


def test_create_shelf_returns_201_with_capacity(client: TestClient, session: Session) -> None:
    response = client.post(URL, json={"name": "Étagère du haut", "rows": 4, "columns": 5})

    assert response.status_code == 201
    body = response.json()
    assert body == {"id": body["id"], "name": "Étagère du haut", "rows": 4, "columns": 5, "capacity": 20}

    shelf_id = UUID(body["id"])  # lève ValueError si l'id renvoyé n'est pas un UUID
    assert shelf_id.version == 4
    entity = session.get(ShelfEntity, shelf_id)
    assert entity is not None
    assert (entity.name, entity.rows, entity.columns) == ("Étagère du haut", 4, 5)


def test_create_shelf_strips_name(client: TestClient) -> None:
    response = client.post(URL, json={"name": "  Étagère du bas  ", "rows": 3, "columns": 4})

    assert response.status_code == 201
    assert response.json()["name"] == "Étagère du bas"


def test_create_shelf_with_existing_name_returns_422(client: TestClient, session: Session) -> None:
    client.post(URL, json={"name": "Cave", "rows": 3, "columns": 4})

    response = client.post(URL, json={"name": "Cave", "rows": 4, "columns": 4})

    assert response.status_code == 422
    assert response.json() == {
        "code": "SHELF_NAME_ALREADY_EXISTS",
        "message": "Une étagère nommée 'Cave' existe déjà",
    }
    assert len(session.exec(select(ShelfEntity)).all()) == 1


@pytest.mark.parametrize("duplicate_name", [" Cave ", "cave", "CAVE", "  cAvE  "])
def test_create_shelf_with_existing_name_ignoring_case_and_spaces_returns_422(
    client: TestClient, session: Session, duplicate_name: str
) -> None:
    client.post(URL, json={"name": "Cave", "rows": 3, "columns": 4})

    response = client.post(URL, json={"name": duplicate_name, "rows": 3, "columns": 4})

    assert response.status_code == 422
    assert response.json()["code"] == "SHELF_NAME_ALREADY_EXISTS"
    assert len(session.exec(select(ShelfEntity)).all()) == 1


def test_create_shelf_with_accented_variant_name_returns_201(client: TestClient) -> None:
    # Seule la casse est ignorée : les accents distinguent deux noms
    client.post(URL, json={"name": "Étagère", "rows": 3, "columns": 4})

    response = client.post(URL, json={"name": "Etagere", "rows": 3, "columns": 4})

    assert response.status_code == 201


@pytest.mark.parametrize(
    ("payload", "invalid_field"),
    [
        ({"name": "Cave", "rows": 0, "columns": 4}, "rows"),
        ({"name": "Cave", "rows": 3, "columns": 0}, "columns"),
        ({"name": "Cave", "rows": -1, "columns": 4}, "rows"),
        ({"name": "Cave", "rows": 51, "columns": 4}, "rows"),
        ({"name": "Cave", "rows": 3, "columns": 51}, "columns"),
        ({"name": "Cave", "rows": "trois", "columns": 4}, "rows"),
        ({"name": "", "rows": 3, "columns": 4}, "name"),
        ({"name": "   ", "rows": 3, "columns": 4}, "name"),
        ({"name": "x" * 101, "rows": 3, "columns": 4}, "name"),
        ({"rows": 3, "columns": 4}, "name"),
        ({"name": "Cave", "columns": 4}, "rows"),
        ({"name": "Cave", "rows": 3}, "columns"),
    ],
)
def test_create_shelf_with_invalid_parameters_returns_400(
    client: TestClient, session: Session, payload: dict, invalid_field: str
) -> None:
    response = client.post(URL, json=payload)

    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "INVALID_PARAMETERS"
    assert [error["loc"] for error in body["details"]] == [["body", invalid_field]]
    assert session.exec(select(ShelfEntity)).all() == []


def test_create_shelf_without_body_returns_400(client: TestClient) -> None:
    response = client.post(URL)

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PARAMETERS"
