from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.factories import create_tag, create_tag_category


def url(category_id: UUID | str) -> str:
    return f"/tag-categories/{category_id}"


def test_update_tag_category_returns_200(client: TestClient, session: Session) -> None:
    category = create_tag_category(session, name="Gout")

    response = client.put(url(category.id), json={"name": "Goût"})

    assert response.status_code == 200
    assert response.json() == {"id": str(category.id), "name": "Goût"}
    session.refresh(category)
    assert category.name == "Goût"


def test_update_tag_category_changing_only_case_returns_200(client: TestClient, session: Session) -> None:
    category = create_tag_category(session, name="goût")

    response = client.put(url(category.id), json={"name": "Goût"})

    assert response.status_code == 200
    assert response.json()["name"] == "Goût"


def test_update_tag_category_keeps_its_tags(client: TestClient, session: Session) -> None:
    category = create_tag_category(session, name="Gout")
    tag = create_tag(session, category, name="fruité")

    client.put(url(category.id), json={"name": "Goût"})

    assert client.get(f"/tags/{tag.id}").json()["category"] == {"id": str(category.id), "name": "Goût"}


@pytest.mark.parametrize("duplicate_name", ["Odeur", "odeur"])
def test_update_tag_category_with_name_of_another_category_returns_422(
    client: TestClient, session: Session, duplicate_name: str
) -> None:
    category = create_tag_category(session, name="Goût")
    create_tag_category(session, name="Odeur")

    response = client.put(url(category.id), json={"name": duplicate_name})

    assert response.status_code == 422
    assert response.json()["code"] == "TAG_CATEGORY_NAME_ALREADY_EXISTS"
    session.refresh(category)
    assert category.name == "Goût"


def test_update_unknown_tag_category_returns_404(client: TestClient) -> None:
    response = client.put(url(uuid4()), json={"name": "Goût"})

    assert response.status_code == 404
    assert response.json()["code"] == "TAG_CATEGORY_NOT_FOUND"


@pytest.mark.parametrize("payload", [{}, {"name": "   "}, {"name": "x" * 51}])
def test_update_tag_category_with_invalid_parameters_returns_400(
    client: TestClient, session: Session, payload: dict
) -> None:
    category = create_tag_category(session, name="Goût")

    response = client.put(url(category.id), json=payload)

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PARAMETERS"
    session.refresh(category)
    assert category.name == "Goût"


def test_update_tag_category_with_non_uuid_id_returns_400(client: TestClient) -> None:
    response = client.put(url("abc"), json={"name": "Goût"})

    assert response.status_code == 400
