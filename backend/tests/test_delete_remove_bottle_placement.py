from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.infrastructure.entity import BottleEntity, BottlePlacementEntity
from tests.factories import create_bottle, create_shelf, place_bottle


def url(bottle_id: UUID | str, placement_id: UUID | str) -> str:
    return f"/bottles/{bottle_id}/placements/{placement_id}"


def test_remove_bottle_placement_returns_204(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    bottle = create_bottle(session)
    placement_id = place_bottle(session, bottle, shelf, row=1, column=1).id
    kept = place_bottle(session, bottle, shelf, row=1, column=2)

    response = client.delete(url(bottle.id, placement_id))

    assert response.status_code == 204
    assert response.content == b""
    session.expire_all()
    assert [p.id for p in session.exec(select(BottlePlacementEntity)).all()] == [kept.id]
    assert client.get(f"/bottles/{bottle.id}").json()["quantity"] == 1


def test_remove_last_placement_keeps_the_bottle(client: TestClient, session: Session) -> None:
    bottle = create_bottle(session)
    placement = place_bottle(session, bottle, create_shelf(session), row=1, column=1)

    client.delete(url(bottle.id, placement.id))

    session.expire_all()
    assert session.get(BottleEntity, bottle.id) is not None
    assert client.get(f"/bottles/{bottle.id}").json()["quantity"] == 0


def test_remove_bottle_placement_frees_the_slot(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    bottle = create_bottle(session)
    placement = place_bottle(session, bottle, shelf, row=1, column=1)

    client.delete(url(bottle.id, placement.id))
    response = client.post(f"/bottles/{bottle.id}/placements", json={"shelf_id": str(shelf.id), "row": 1, "column": 1})

    assert response.status_code == 201


def test_remove_placement_of_another_bottle_returns_404(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    bottle = create_bottle(session, cuvee="A")
    other_placement = place_bottle(session, create_bottle(session, cuvee="B"), shelf, row=1, column=1)

    response = client.delete(url(bottle.id, other_placement.id))

    assert response.status_code == 404
    assert response.json()["code"] == "PLACEMENT_NOT_FOUND"
    session.expire_all()
    assert session.get(BottlePlacementEntity, other_placement.id) is not None


def test_remove_placement_already_removed_returns_404(client: TestClient, session: Session) -> None:
    bottle = create_bottle(session)
    placement_id = place_bottle(session, bottle, create_shelf(session), row=1, column=1).id
    client.delete(url(bottle.id, placement_id))

    response = client.delete(url(bottle.id, placement_id))

    assert response.status_code == 404
    assert response.json()["code"] == "PLACEMENT_NOT_FOUND"


def test_remove_placement_of_unknown_bottle_returns_404(client: TestClient) -> None:
    response = client.delete(url(uuid4(), uuid4()))

    assert response.status_code == 404
    assert response.json()["code"] == "BOTTLE_NOT_FOUND"


def test_remove_bottle_placement_with_non_uuid_ids_returns_400(client: TestClient, session: Session) -> None:
    bottle = create_bottle(session)

    assert client.delete(url("abc", uuid4())).status_code == 400
    assert client.delete(url(bottle.id, "abc")).status_code == 400
