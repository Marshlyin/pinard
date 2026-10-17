from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.infrastructure.entity import TagEntity
from tests.factories import create_tag, create_tag_category

URL = "/tags"


def test_create_tag_returns_201_with_its_category(client: TestClient, session: Session) -> None:
    category = create_tag_category(session, name="Goût")

    response = client.post(URL, json={"name": "fruité", "category_id": str(category.id), "color": "#c0392b"})

    assert response.status_code == 201
    body = response.json()
    assert body == {
        "id": body["id"],
        "name": "fruité",
        "color": "#c0392b",
        "category": {"id": str(category.id), "name": "Goût"},
    }
    entity = session.get(TagEntity, UUID(body["id"]))
    assert entity is not None
    assert (entity.name, entity.category_id, entity.color) == ("fruité", category.id, "#c0392b")


def test_create_tag_without_color_uses_default_grey(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)

    response = client.post(URL, json={"name": "fruité", "category_id": str(category.id)})

    assert response.status_code == 201
    assert response.json()["color"] == "#9e9e9e"


def test_create_tag_normalizes_color_to_lowercase(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)

    response = client.post(URL, json={"name": "fruité", "category_id": str(category.id), "color": "#C0392B"})

    assert response.status_code == 201
    assert response.json()["color"] == "#c0392b"


@pytest.mark.parametrize("invalid_color", ["red", "c0392b", "#fff", "#c0392b80", "#gggggg", "", "  "])
def test_create_tag_with_invalid_color_returns_400(client: TestClient, session: Session, invalid_color: str) -> None:
    category = create_tag_category(session)

    response = client.post(URL, json={"name": "fruité", "category_id": str(category.id), "color": invalid_color})

    assert response.status_code == 400
    assert [error["loc"] for error in response.json()["details"]] == [["body", "color"]]
    assert session.exec(select(TagEntity)).all() == []


def test_create_tag_strips_name(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)

    response = client.post(URL, json={"name": "  boisé ", "category_id": str(category.id)})

    assert response.status_code == 201
    assert response.json()["name"] == "boisé"


def test_create_tag_with_same_name_in_another_category_returns_201(client: TestClient, session: Session) -> None:
    create_tag(session, create_tag_category(session, name="Goût"), name="fruité")
    odeur = create_tag_category(session, name="Odeur")

    response = client.post(URL, json={"name": "fruité", "category_id": str(odeur.id)})

    assert response.status_code == 201


@pytest.mark.parametrize("duplicate_name", ["fruité", "Fruité", "FRUITÉ"])
def test_create_tag_with_existing_name_in_category_returns_422(
    client: TestClient, session: Session, duplicate_name: str
) -> None:
    category = create_tag_category(session, name="Goût")
    create_tag(session, category, name="fruité")

    response = client.post(URL, json={"name": duplicate_name, "category_id": str(category.id)})

    assert response.status_code == 422
    assert response.json() == {
        "code": "TAG_NAME_ALREADY_EXISTS",
        "message": f"Une étiquette nommée '{duplicate_name}' existe déjà dans la catégorie 'Goût'",
    }
    assert len(session.exec(select(TagEntity)).all()) == 1


def test_create_tag_with_unknown_category_returns_422(client: TestClient, session: Session) -> None:
    unknown_id = uuid4()

    response = client.post(URL, json={"name": "fruité", "category_id": str(unknown_id)})

    assert response.status_code == 422
    assert response.json() == {
        "code": "UNKNOWN_TAG_CATEGORY",
        "message": f"Aucune catégorie d'étiquettes avec l'identifiant {unknown_id}",
    }
    assert session.exec(select(TagEntity)).all() == []


@pytest.mark.parametrize(
    ("payload", "invalid_field"),
    [
        ({"category_id": "00000000-0000-4000-8000-000000000000"}, "name"),
        ({"name": "   ", "category_id": "00000000-0000-4000-8000-000000000000"}, "name"),
        ({"name": "x" * 51, "category_id": "00000000-0000-4000-8000-000000000000"}, "name"),
        ({"name": "fruité"}, "category_id"),
        ({"name": "fruité", "category_id": "abc"}, "category_id"),
    ],
)
def test_create_tag_with_invalid_parameters_returns_400(
    client: TestClient, session: Session, payload: dict, invalid_field: str
) -> None:
    response = client.post(URL, json=payload)

    assert response.status_code == 400
    assert [error["loc"] for error in response.json()["details"]] == [["body", invalid_field]]
    assert session.exec(select(TagEntity)).all() == []
