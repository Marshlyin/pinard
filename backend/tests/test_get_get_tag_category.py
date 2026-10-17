from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.factories import create_tag_category


def url(category_id: UUID | str) -> str:
    return f"/tag-categories/{category_id}"


def test_get_tag_category_returns_200(client: TestClient, session: Session) -> None:
    category = create_tag_category(session, name="Goût")

    response = client.get(url(category.id))

    assert response.status_code == 200
    assert response.json() == {"id": str(category.id), "name": "Goût"}


def test_get_unknown_tag_category_returns_404(client: TestClient) -> None:
    unknown_id = uuid4()

    response = client.get(url(unknown_id))

    assert response.status_code == 404
    assert response.json() == {
        "code": "TAG_CATEGORY_NOT_FOUND",
        "message": f"Aucune catégorie d'étiquettes avec l'identifiant {unknown_id}",
    }


def test_get_tag_category_with_non_uuid_id_returns_400(client: TestClient) -> None:
    response = client.get(url("abc"))

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PARAMETERS"
