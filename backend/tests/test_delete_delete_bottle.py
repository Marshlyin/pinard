from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.infrastructure.entity import BottleEntity, BottlePlacementEntity, BottleTagLink, ShelfEntity, TagEntity
from tests.factories import create_bottle, create_shelf, create_tag, create_tag_category, place_bottle, tag_bottle


def url(bottle_id: UUID | str) -> str:
    return f"/bottles/{bottle_id}"


def test_delete_bottle_returns_204(client: TestClient, session: Session) -> None:
    bottle_id = create_bottle(session, cuvee="A").id
    other = create_bottle(session, cuvee="B")

    response = client.delete(url(bottle_id))

    assert response.status_code == 204
    assert response.content == b""
    session.expire_all()
    assert [b.id for b in session.exec(select(BottleEntity)).all()] == [other.id]


def test_delete_bottle_deletes_its_placements_and_tag_links_only(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    tag = create_tag(session, create_tag_category(session))
    bottle = create_bottle(session, cuvee="A")
    other = create_bottle(session, cuvee="B")
    place_bottle(session, bottle, shelf, row=1, column=1)
    place_bottle(session, bottle, shelf, row=1, column=2)
    other_placement = place_bottle(session, other, shelf, row=2, column=1)
    tag_bottle(session, bottle, tag)
    tag_bottle(session, other, tag)

    response = client.delete(url(bottle.id))

    assert response.status_code == 204
    session.expire_all()
    assert [p.id for p in session.exec(select(BottlePlacementEntity)).all()] == [other_placement.id]
    assert [link.bottle_id for link in session.exec(select(BottleTagLink)).all()] == [other.id]
    assert session.get(ShelfEntity, shelf.id) is not None
    assert session.get(TagEntity, tag.id) is not None


def test_delete_unknown_bottle_returns_404(client: TestClient) -> None:
    response = client.delete(url(uuid4()))

    assert response.status_code == 404
    assert response.json()["code"] == "BOTTLE_NOT_FOUND"


def test_delete_bottle_with_non_uuid_id_returns_400(client: TestClient) -> None:
    response = client.delete(url("abc"))

    assert response.status_code == 400
