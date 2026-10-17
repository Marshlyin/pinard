from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.infrastructure.entity import TagCategoryEntity
from tests.factories import create_tag_category

URL = "/tag-categories"


def test_create_tag_category_returns_201(client: TestClient, session: Session) -> None:
    response = client.post(URL, json={"name": "Goût"})

    assert response.status_code == 201
    body = response.json()
    assert body == {"id": body["id"], "name": "Goût"}
    entity = session.get(TagCategoryEntity, UUID(body["id"]))
    assert entity is not None
    assert entity.name == "Goût"


def test_create_tag_category_strips_name(client: TestClient) -> None:
    response = client.post(URL, json={"name": "  Garde  "})

    assert response.status_code == 201
    assert response.json()["name"] == "Garde"


@pytest.mark.parametrize("duplicate_name", ["Goût", "goût", "GOÛT", " Goût "])
def test_create_tag_category_with_existing_name_returns_422(
    client: TestClient, session: Session, duplicate_name: str
) -> None:
    create_tag_category(session, name="Goût")

    response = client.post(URL, json={"name": duplicate_name})

    assert response.status_code == 422
    assert response.json()["code"] == "TAG_CATEGORY_NAME_ALREADY_EXISTS"
    assert len(session.exec(select(TagCategoryEntity)).all()) == 1


@pytest.mark.parametrize("payload", [{}, {"name": ""}, {"name": "   "}, {"name": "x" * 51}, {"name": 12}])
def test_create_tag_category_with_invalid_parameters_returns_400(
    client: TestClient, session: Session, payload: dict
) -> None:
    response = client.post(URL, json=payload)

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PARAMETERS"
    assert session.exec(select(TagCategoryEntity)).all() == []
