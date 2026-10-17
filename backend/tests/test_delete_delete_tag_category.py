from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.infrastructure.entity import TagCategoryEntity, TagEntity
from tests.factories import create_tag, create_tag_category


def url(category_id: UUID | str) -> str:
    return f"/tag-categories/{category_id}"


def test_delete_empty_tag_category_returns_204(client: TestClient, session: Session) -> None:
    category_id = create_tag_category(session, name="Goût").id
    other = create_tag_category(session, name="Odeur")

    response = client.delete(url(category_id))

    assert response.status_code == 204
    assert response.content == b""
    session.expire_all()
    assert [c.id for c in session.exec(select(TagCategoryEntity)).all()] == [other.id]


def test_delete_tag_category_containing_tags_returns_422(client: TestClient, session: Session) -> None:
    category = create_tag_category(session, name="Goût")
    create_tag(session, category, name="fruité")
    create_tag(session, category, name="boisé")

    response = client.delete(url(category.id))

    assert response.status_code == 422
    assert response.json() == {
        "code": "TAG_CATEGORY_NOT_EMPTY",
        "message": "Impossible de supprimer la catégorie 'Goût' : elle contient encore 2 étiquette(s)",
    }
    session.expire_all()
    assert session.get(TagCategoryEntity, category.id) is not None
    assert len(session.exec(select(TagEntity)).all()) == 2


def test_delete_unknown_tag_category_returns_404(client: TestClient) -> None:
    response = client.delete(url(uuid4()))

    assert response.status_code == 404
    assert response.json()["code"] == "TAG_CATEGORY_NOT_FOUND"


def test_delete_tag_category_with_non_uuid_id_returns_400(client: TestClient) -> None:
    response = client.delete(url("abc"))

    assert response.status_code == 400
