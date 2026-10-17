from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.infrastructure.entity import BottleEntity, BottleTagLink, TagCategoryEntity, TagEntity
from tests.factories import create_bottle, create_tag, create_tag_category, tag_bottle


def url(tag_id: UUID | str) -> str:
    return f"/tags/{tag_id}"


def test_delete_tag_returns_204(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)
    tag_id = create_tag(session, category, name="fruité").id
    other = create_tag(session, category, name="boisé")

    response = client.delete(url(tag_id))

    assert response.status_code == 204
    assert response.content == b""
    session.expire_all()
    assert [t.id for t in session.exec(select(TagEntity)).all()] == [other.id]
    assert session.get(TagCategoryEntity, category.id) is not None


def test_delete_tag_removes_it_from_bottles_but_keeps_bottles(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)
    tag = create_tag(session, category, name="fruité")
    other_tag = create_tag(session, category, name="boisé")
    bottle = create_bottle(session)
    tag_bottle(session, bottle, tag)
    tag_bottle(session, bottle, other_tag)

    response = client.delete(url(tag.id))

    assert response.status_code == 204
    session.expire_all()
    assert session.get(BottleEntity, bottle.id) is not None
    assert [(link.bottle_id, link.tag_id) for link in session.exec(select(BottleTagLink)).all()] == [
        (bottle.id, other_tag.id)
    ]


def test_delete_unknown_tag_returns_404(client: TestClient) -> None:
    response = client.delete(url(uuid4()))

    assert response.status_code == 404
    assert response.json()["code"] == "TAG_NOT_FOUND"


def test_delete_tag_with_non_uuid_id_returns_400(client: TestClient) -> None:
    response = client.delete(url("abc"))

    assert response.status_code == 400
