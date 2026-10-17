from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.factories import create_bottle, create_shelf, create_tag, create_tag_category, place_bottle, tag_bottle


def url(bottle_id: UUID | str) -> str:
    return f"/bottles/{bottle_id}"


def test_get_bottle_without_tag_nor_placement(client: TestClient, session: Session) -> None:
    bottle = create_bottle(session, cuvee="Les Picasses", domain="Olga Raffault", vintage=2020)

    response = client.get(url(bottle.id))

    assert response.status_code == 200
    assert response.json() == {
        "id": str(bottle.id),
        "cuvee": "Les Picasses",
        "domain": "Olga Raffault",
        "vintage": 2020,
        "quantity": 0,
        "tags": [],
        "placements": [],
    }


def test_get_bottle_returns_placements_sorted_by_shelf_row_column(client: TestClient, session: Session) -> None:
    cave = create_shelf(session, name="Cave")
    garage = create_shelf(session, name="Garage")
    bottle = create_bottle(session)
    garage_1_1 = place_bottle(session, bottle, garage, row=1, column=1)
    cave_2_1 = place_bottle(session, bottle, cave, row=2, column=1)
    cave_1_3 = place_bottle(session, bottle, cave, row=1, column=3)

    response = client.get(url(bottle.id))

    assert response.status_code == 200
    assert response.json()["quantity"] == 3
    cave_json = {"id": str(cave.id), "name": "Cave"}
    assert response.json()["placements"] == [
        {"id": str(cave_1_3.id), "shelf": cave_json, "row": 1, "column": 3},
        {"id": str(cave_2_1.id), "shelf": cave_json, "row": 2, "column": 1},
        {"id": str(garage_1_1.id), "shelf": {"id": str(garage.id), "name": "Garage"}, "row": 1, "column": 1},
    ]


def test_get_bottle_returns_only_its_own_tags_and_placements(client: TestClient, session: Session) -> None:
    category = create_tag_category(session)
    fruite = create_tag(session, category, name="fruité")
    boise = create_tag(session, category, name="boisé")
    shelf = create_shelf(session)
    bottle = create_bottle(session, cuvee="A")
    other = create_bottle(session, cuvee="B")
    tag_bottle(session, bottle, fruite)
    tag_bottle(session, other, boise)
    place_bottle(session, bottle, shelf, row=1, column=1)
    place_bottle(session, other, shelf, row=1, column=2)

    body = client.get(url(bottle.id)).json()

    assert [tag["name"] for tag in body["tags"]] == ["fruité"]
    assert [(p["row"], p["column"]) for p in body["placements"]] == [(1, 1)]


def test_get_unknown_bottle_returns_404(client: TestClient) -> None:
    unknown_id = uuid4()

    response = client.get(url(unknown_id))

    assert response.status_code == 404
    assert response.json() == {
        "code": "BOTTLE_NOT_FOUND",
        "message": f"Aucune bouteille avec l'identifiant {unknown_id}",
    }


def test_get_bottle_with_non_uuid_id_returns_400(client: TestClient) -> None:
    response = client.get(url("abc"))

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PARAMETERS"
