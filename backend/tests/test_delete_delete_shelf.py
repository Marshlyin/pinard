from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.infrastructure.entity import BottleEntity, BottlePlacementEntity, ShelfEntity
from tests.factories import create_bottle, create_shelf, place_bottle


def url(shelf_id: UUID | str) -> str:
    return f"/shelves/{shelf_id}"


def test_delete_empty_shelf_returns_204(client: TestClient, session: Session) -> None:
    shelf_id = create_shelf(session).id

    response = client.delete(url(shelf_id))

    assert response.status_code == 204
    assert response.content == b""
    session.expire_all()
    assert session.get(ShelfEntity, shelf_id) is None


def test_delete_shelf_only_deletes_targeted_shelf(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, name="Cave")
    other_shelf = create_shelf(session, name="Garage")

    client.delete(url(shelf.id))

    session.expire_all()
    assert [s.id for s in session.exec(select(ShelfEntity)).all()] == [other_shelf.id]


def test_delete_shelf_containing_bottles_returns_422(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, name="Cave")
    bottle = create_bottle(session)
    place_bottle(session, bottle, shelf, row=1, column=1)
    place_bottle(session, bottle, shelf, row=2, column=3)

    response = client.delete(url(shelf.id))

    assert response.status_code == 422
    assert response.json() == {
        "code": "SHELF_NOT_EMPTY",
        "message": "Impossible de supprimer l'étagère 'Cave' : elle contient encore 2 bouteille(s)",
    }
    session.expire_all()
    assert session.get(ShelfEntity, shelf.id) is not None
    assert len(session.exec(select(BottlePlacementEntity)).all()) == 2
    assert session.get(BottleEntity, bottle.id) is not None


def test_delete_shelf_already_deleted_returns_404(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    client.delete(url(shelf.id))

    response = client.delete(url(shelf.id))

    assert response.status_code == 404
    assert response.json()["code"] == "SHELF_NOT_FOUND"


def test_delete_unknown_shelf_returns_404(client: TestClient) -> None:
    unknown_id = uuid4()

    response = client.delete(url(unknown_id))

    assert response.status_code == 404
    assert response.json() == {"code": "SHELF_NOT_FOUND", "message": f"Aucune étagère avec l'identifiant {unknown_id}"}


def test_delete_shelf_with_non_uuid_id_returns_400(client: TestClient) -> None:
    response = client.delete(url("abc"))

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PARAMETERS"
