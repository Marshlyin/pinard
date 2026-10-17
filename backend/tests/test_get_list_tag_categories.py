from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.factories import create_tag_category

URL = "/tag-categories"


def test_list_tag_categories_without_category_returns_empty_list(client: TestClient) -> None:
    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() == []


def test_list_tag_categories_returns_categories_sorted_by_name(client: TestClient, session: Session) -> None:
    type_ = create_tag_category(session, name="Type")
    garde = create_tag_category(session, name="Garde")
    gout = create_tag_category(session, name="Goût")

    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() == [
        {"id": str(garde.id), "name": "Garde"},
        {"id": str(gout.id), "name": "Goût"},
        {"id": str(type_.id), "name": "Type"},
    ]
