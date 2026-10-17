from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.factories import create_bottle, create_tag, create_tag_category, tag_bottle


def url(tag_id: UUID | str) -> str:
    return f"/tags/{tag_id}"


def body(name: str, category_id: UUID | str, color: str = "#9e9e9e") -> dict:
    return {"name": name, "category_id": str(category_id), "color": color}


def test_update_tag_returns_200(client: TestClient, session: Session) -> None:
    category = create_tag_category(session, name="Goût")
    tag = create_tag(session, category, name="fruite", color="#9e9e9e")

    response = client.put(url(tag.id), json=body("fruité", category.id, color="#c0392b"))

    assert response.status_code == 200
    assert response.json() == {
        "id": str(tag.id),
        "name": "fruité",
        "color": "#c0392b",
        "category": {"id": str(category.id), "name": "Goût"},
    }
    session.refresh(tag)
    assert (tag.name, tag.color) == ("fruité", "#c0392b")


def test_update_tag_normalizes_color_to_lowercase(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)
    tag = create_tag(session, category)

    response = client.put(url(tag.id), json=body("fruité", category.id, color="#C0392B"))

    assert response.status_code == 200
    assert response.json()["color"] == "#c0392b"


def test_update_tag_moves_it_to_another_category(client: TestClient, session: Session) -> None:
    tag = create_tag(session, create_tag_category(session, name="Goût"), name="fruité")
    odeur = create_tag_category(session, name="Odeur")

    response = client.put(url(tag.id), json=body("fruité", odeur.id))

    assert response.status_code == 200
    assert response.json()["category"] == {"id": str(odeur.id), "name": "Odeur"}
    session.refresh(tag)
    assert tag.category_id == odeur.id


def test_update_tag_changing_only_case_returns_200(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)
    tag = create_tag(session, category, name="fruité")

    response = client.put(url(tag.id), json=body("Fruité", category.id))

    assert response.status_code == 200
    assert response.json()["name"] == "Fruité"


def test_update_tag_keeps_its_bottles(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)
    tag = create_tag(session, category, name="fruite")
    bottle = create_bottle(session)
    tag_bottle(session, bottle, tag)

    client.put(url(tag.id), json=body("fruité", category.id))

    assert [b["id"] for b in client.get(url(tag.id)).json()["bottles"]] == [str(bottle.id)]


@pytest.mark.parametrize("duplicate_name", ["boisé", "Boisé"])
def test_update_tag_with_name_of_another_tag_in_category_returns_422(
    client: TestClient, session: Session, duplicate_name: str
) -> None:
    category = create_tag_category(session, name="Goût")
    tag = create_tag(session, category, name="fruité")
    create_tag(session, category, name="boisé")

    response = client.put(url(tag.id), json=body(duplicate_name, category.id))

    assert response.status_code == 422
    assert response.json()["code"] == "TAG_NAME_ALREADY_EXISTS"
    session.refresh(tag)
    assert tag.name == "fruité"


def test_update_tag_moving_to_category_with_same_name_returns_422(client: TestClient, session: Session) -> None:
    tag = create_tag(session, create_tag_category(session, name="Goût"), name="fruité")
    odeur = create_tag_category(session, name="Odeur")
    create_tag(session, odeur, name="Fruité")

    response = client.put(url(tag.id), json=body("fruité", odeur.id))

    assert response.status_code == 422
    assert response.json() == {
        "code": "TAG_NAME_ALREADY_EXISTS",
        "message": "Une étiquette nommée 'fruité' existe déjà dans la catégorie 'Odeur'",
    }


def test_update_tag_with_unknown_category_returns_422(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)
    tag = create_tag(session, category)

    response = client.put(url(tag.id), json=body("fruité", uuid4()))

    assert response.status_code == 422
    assert response.json()["code"] == "UNKNOWN_TAG_CATEGORY"
    session.refresh(tag)
    assert tag.category_id == category.id


def test_update_unknown_tag_returns_404(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)

    response = client.put(url(uuid4()), json=body("fruité", category.id))

    assert response.status_code == 404
    assert response.json()["code"] == "TAG_NOT_FOUND"


VALID_CATEGORY_ID = "00000000-0000-4000-8000-000000000000"


@pytest.mark.parametrize(
    ("payload", "invalid_field"),
    [
        ({"name": "   ", "category_id": VALID_CATEGORY_ID, "color": "#9e9e9e"}, "name"),
        ({"name": "fruité", "color": "#9e9e9e"}, "category_id"),
        ({"name": "fruité", "category_id": "abc", "color": "#9e9e9e"}, "category_id"),
        ({"name": "fruité", "category_id": VALID_CATEGORY_ID}, "color"),  # couleur obligatoire en modification
        ({"name": "fruité", "category_id": VALID_CATEGORY_ID, "color": "red"}, "color"),
        ({"name": "fruité", "category_id": VALID_CATEGORY_ID, "color": "#fff"}, "color"),
    ],
)
def test_update_tag_with_invalid_parameters_returns_400(
    client: TestClient, session: Session, payload: dict, invalid_field: str
) -> None:
    tag = create_tag(session, create_tag_category(session), name="fruité", color="#123456")

    response = client.put(url(tag.id), json=payload)

    assert response.status_code == 400
    assert [error["loc"] for error in response.json()["details"]] == [["body", invalid_field]]
    session.refresh(tag)
    assert tag.color == "#123456"


def test_update_tag_with_non_uuid_id_returns_400(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)

    response = client.put(url("abc"), json=body("fruité", category.id))

    assert response.status_code == 400
