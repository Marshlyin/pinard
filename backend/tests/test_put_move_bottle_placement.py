from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.factories import create_bottle, create_shelf, place_bottle


def url(bottle_id: UUID | str, placement_id: UUID | str) -> str:
    return f"/bottles/{bottle_id}/placements/{placement_id}"


def test_move_bottle_placement_in_same_shelf_returns_200(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, name="Cave")
    bottle = create_bottle(session)
    placement = place_bottle(session, bottle, shelf, row=1, column=1)

    response = client.put(url(bottle.id, placement.id), json={"shelf_id": str(shelf.id), "row": 3, "column": 4})

    assert response.status_code == 200
    assert response.json() == {
        "id": str(placement.id),
        "shelf": {"id": str(shelf.id), "name": "Cave"},
        "row": 3,
        "column": 4,
    }
    session.refresh(placement)
    assert (placement.row, placement.column) == (3, 4)


def test_move_bottle_placement_to_another_shelf_returns_200(client: TestClient, session: Session) -> None:
    cave = create_shelf(session, name="Cave")
    garage = create_shelf(session, name="Garage")
    bottle = create_bottle(session)
    placement = place_bottle(session, bottle, cave, row=1, column=1)

    response = client.put(url(bottle.id, placement.id), json={"shelf_id": str(garage.id), "row": 2, "column": 2})

    assert response.status_code == 200
    assert response.json()["shelf"] == {"id": str(garage.id), "name": "Garage"}
    assert client.get(f"/shelves/{cave.id}").json()["placements"] == []
    assert [p["id"] for p in client.get(f"/shelves/{garage.id}").json()["placements"]] == [str(placement.id)]


def test_move_bottle_placement_to_its_own_slot_returns_200(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    bottle = create_bottle(session)
    placement = place_bottle(session, bottle, shelf, row=1, column=1)

    response = client.put(url(bottle.id, placement.id), json={"shelf_id": str(shelf.id), "row": 1, "column": 1})

    assert response.status_code == 200


def test_move_bottle_placement_to_occupied_slot_returns_422(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, name="Cave")
    bottle = create_bottle(session, cuvee="A")
    placement = place_bottle(session, bottle, shelf, row=1, column=1)
    place_bottle(session, create_bottle(session, cuvee="B", domain="Domaine B"), shelf, row=2, column=2)

    response = client.put(url(bottle.id, placement.id), json={"shelf_id": str(shelf.id), "row": 2, "column": 2})

    assert response.status_code == 422
    assert response.json()["code"] == "SLOT_ALREADY_OCCUPIED"
    session.refresh(placement)
    assert (placement.row, placement.column) == (1, 1)


def test_move_bottle_placement_to_slot_occupied_by_same_bottle_returns_422(
    client: TestClient, session: Session
) -> None:
    shelf = create_shelf(session)
    bottle = create_bottle(session)
    placement = place_bottle(session, bottle, shelf, row=1, column=1)
    place_bottle(session, bottle, shelf, row=1, column=2)

    response = client.put(url(bottle.id, placement.id), json={"shelf_id": str(shelf.id), "row": 1, "column": 2})

    assert response.status_code == 422
    assert response.json()["code"] == "SLOT_ALREADY_OCCUPIED"


def test_move_bottle_placement_outside_shelf_returns_422(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session, rows=3, columns=4)
    bottle = create_bottle(session)
    placement = place_bottle(session, bottle, shelf, row=1, column=1)

    response = client.put(url(bottle.id, placement.id), json={"shelf_id": str(shelf.id), "row": 4, "column": 1})

    assert response.status_code == 422
    assert response.json()["code"] == "SLOT_OUTSIDE_SHELF"


def test_move_bottle_placement_to_unknown_shelf_returns_422(client: TestClient, session: Session) -> None:
    bottle = create_bottle(session)
    placement = place_bottle(session, bottle, create_shelf(session), row=1, column=1)

    response = client.put(url(bottle.id, placement.id), json={"shelf_id": str(uuid4()), "row": 1, "column": 1})

    assert response.status_code == 422
    assert response.json()["code"] == "UNKNOWN_SHELF"


def test_move_placement_of_another_bottle_returns_404(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    bottle = create_bottle(session, cuvee="A")
    other = create_bottle(session, cuvee="B")
    other_placement = place_bottle(session, other, shelf, row=1, column=1)

    response = client.put(url(bottle.id, other_placement.id), json={"shelf_id": str(shelf.id), "row": 2, "column": 2})

    assert response.status_code == 404
    assert response.json() == {
        "code": "PLACEMENT_NOT_FOUND",
        "message": f"Aucun emplacement {other_placement.id} pour la bouteille {bottle.id}",
    }
    session.refresh(other_placement)
    assert (other_placement.row, other_placement.column) == (1, 1)


def test_move_unknown_placement_returns_404(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    bottle = create_bottle(session)

    response = client.put(url(bottle.id, uuid4()), json={"shelf_id": str(shelf.id), "row": 1, "column": 1})

    assert response.status_code == 404
    assert response.json()["code"] == "PLACEMENT_NOT_FOUND"


def test_move_placement_of_unknown_bottle_returns_404(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    placement = place_bottle(session, create_bottle(session), shelf, row=1, column=1)

    response = client.put(url(uuid4(), placement.id), json={"shelf_id": str(shelf.id), "row": 2, "column": 2})

    assert response.status_code == 404
    assert response.json()["code"] == "BOTTLE_NOT_FOUND"


def test_move_bottle_placement_with_invalid_parameters_returns_400(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    bottle = create_bottle(session)
    placement = place_bottle(session, bottle, shelf, row=1, column=1)

    response = client.put(url(bottle.id, placement.id), json={"shelf_id": str(shelf.id), "row": 0, "column": 1})

    assert response.status_code == 400
    assert response.json()["details"][0]["loc"] == ["body", "row"]


def test_move_bottle_placement_with_non_uuid_placement_id_returns_400(client: TestClient, session: Session) -> None:
    shelf = create_shelf(session)
    bottle = create_bottle(session)

    response = client.put(url(bottle.id, "abc"), json={"shelf_id": str(shelf.id), "row": 1, "column": 1})

    assert response.status_code == 400
    assert response.json()["details"][0]["loc"] == ["path", "placement_id"]
