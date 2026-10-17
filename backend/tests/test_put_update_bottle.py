from collections.abc import Sequence
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.infrastructure.entity import BottleTagLink, TagEntity
from tests.factories import create_bottle, create_shelf, create_tag, create_tag_category, place_bottle, tag_bottle


def url(bottle_id: UUID | str) -> str:
    return f"/bottles/{bottle_id}"


def payload(
    cuvee: str = "Les Picasses",
    domain: str = "Olga Raffault",
    vintage: int | None = 2020,
    tag_ids: Sequence[UUID] = (),
) -> dict:
    return {"cuvee": cuvee, "domain": domain, "vintage": vintage, "tag_ids": [str(tag_id) for tag_id in tag_ids]}


def test_update_bottle_returns_200(client: TestClient, session: Session) -> None:
    bottle = create_bottle(session, cuvee="Picasses", domain="Raffault", vintage=2019)

    response = client.put(url(bottle.id), json=payload())

    assert response.status_code == 200
    assert response.json() == {
        "id": str(bottle.id),
        "cuvee": "Les Picasses",
        "domain": "Olga Raffault",
        "vintage": 2020,
        "quantity": 0,
        "tags": [],
    }
    session.refresh(bottle)
    assert (bottle.cuvee, bottle.domain, bottle.vintage) == ("Les Picasses", "Olga Raffault", 2020)


def test_update_bottle_can_remove_vintage(client: TestClient, session: Session) -> None:
    bottle = create_bottle(session, vintage=2020)

    response = client.put(url(bottle.id), json=payload(vintage=None))

    assert response.status_code == 200
    assert response.json()["vintage"] is None


def test_update_bottle_replaces_its_tags(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)
    fruite = create_tag(session, category, name="fruité")
    boise = create_tag(session, category, name="boisé")
    epice = create_tag(session, category, name="épicé")
    bottle = create_bottle(session)
    tag_bottle(session, bottle, fruite)
    tag_bottle(session, bottle, boise)

    response = client.put(url(bottle.id), json=payload(tag_ids=[boise.id, epice.id]))

    assert response.status_code == 200
    assert [tag["name"] for tag in response.json()["tags"]] == ["boisé", "épicé"]
    session.expire_all()
    assert {link.tag_id for link in session.exec(select(BottleTagLink)).all()} == {boise.id, epice.id}


def test_update_bottle_with_empty_tag_list_removes_all_tags_but_keeps_them(
    client: TestClient, session: Session
) -> None:
    tag = create_tag(session, create_tag_category(session))
    bottle = create_bottle(session)
    tag_bottle(session, bottle, tag)

    response = client.put(url(bottle.id), json=payload(tag_ids=[]))

    assert response.status_code == 200
    assert response.json()["tags"] == []
    session.expire_all()
    assert session.exec(select(BottleTagLink)).all() == []
    assert session.get(TagEntity, tag.id) is not None


def test_update_bottle_keeps_its_placements(client: TestClient, session: Session) -> None:
    bottle = create_bottle(session)
    place_bottle(session, bottle, create_shelf(session), row=1, column=1)

    response = client.put(url(bottle.id), json=payload(cuvee="Nouvelle cuvée"))

    assert response.status_code == 200
    assert response.json()["quantity"] == 1


def test_update_bottle_changing_only_case_returns_200(client: TestClient, session: Session) -> None:
    bottle = create_bottle(session, cuvee="les picasses", domain="olga raffault", vintage=2020)

    response = client.put(url(bottle.id), json=payload())

    assert response.status_code == 200
    assert response.json()["cuvee"] == "Les Picasses"


@pytest.mark.parametrize("cuvee", ["Les Picasses", "LES PICASSES"])
def test_update_bottle_same_as_another_bottle_returns_422(client: TestClient, session: Session, cuvee: str) -> None:
    create_bottle(session, cuvee="Les Picasses", domain="Olga Raffault", vintage=2020)
    bottle = create_bottle(session, cuvee="Les Barnabés", domain="Olga Raffault", vintage=2020)

    response = client.put(url(bottle.id), json=payload(cuvee=cuvee))

    assert response.status_code == 422
    assert response.json()["code"] == "BOTTLE_ALREADY_EXISTS"
    session.refresh(bottle)
    assert bottle.cuvee == "Les Barnabés"


def test_update_bottle_with_unknown_tags_returns_422_and_keeps_tags(client: TestClient, session: Session) -> None:
    tag = create_tag(session, create_tag_category(session))
    bottle = create_bottle(session)
    tag_bottle(session, bottle, tag)
    unknown_id = uuid4()

    response = client.put(url(bottle.id), json=payload(tag_ids=[unknown_id]))

    assert response.status_code == 422
    assert response.json() == {"code": "UNKNOWN_TAGS", "message": f"Étiquette(s) inexistante(s) : {unknown_id}"}
    session.expire_all()
    assert [link.tag_id for link in session.exec(select(BottleTagLink)).all()] == [tag.id]


def test_update_unknown_bottle_returns_404(client: TestClient) -> None:
    response = client.put(url(uuid4()), json=payload())

    assert response.status_code == 404
    assert response.json()["code"] == "BOTTLE_NOT_FOUND"


@pytest.mark.parametrize(
    ("body", "invalid_field"),
    [
        ({"cuvee": "Les Picasses", "domain": "Olga Raffault", "vintage": 2020}, "tag_ids"),  # tag_ids obligatoire
        ({"cuvee": "   ", "domain": "Olga Raffault", "tag_ids": []}, "cuvee"),
        ({"cuvee": "Les Picasses", "domain": "Olga Raffault", "vintage": 1700, "tag_ids": []}, "vintage"),
    ],
)
def test_update_bottle_with_invalid_parameters_returns_400(
    client: TestClient, session: Session, body: dict, invalid_field: str
) -> None:
    bottle = create_bottle(session, cuvee="Les Picasses")

    response = client.put(url(bottle.id), json=body)

    assert response.status_code == 400
    assert [error["loc"] for error in response.json()["details"]] == [["body", invalid_field]]


def test_update_bottle_with_non_uuid_id_returns_400(client: TestClient) -> None:
    response = client.put(url("abc"), json=payload())

    assert response.status_code == 400
