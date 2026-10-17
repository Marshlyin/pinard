from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.factories import create_bottle, create_tag, create_tag_category, tag_bottle

URL = "/tags"


def test_list_tags_without_tag_returns_empty_list(client: TestClient) -> None:
    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() == []


def test_list_tags_returns_tags_sorted_by_category_then_name(client: TestClient, session: Session) -> None:
    odeur = create_tag_category(session, name="Odeur")
    gout = create_tag_category(session, name="Goût")
    vanille = create_tag(session, odeur, name="vanille", color="#f3e5ab")
    fruite = create_tag(session, gout, name="fruité", color="#c0392b")
    boise = create_tag(session, gout, name="boisé", color="#8b5a2b")

    response = client.get(URL)

    assert response.status_code == 200
    gout_json = {"id": str(gout.id), "name": "Goût"}
    odeur_json = {"id": str(odeur.id), "name": "Odeur"}
    assert response.json() == [
        {"id": str(boise.id), "name": "boisé", "color": "#8b5a2b", "category": gout_json},
        {"id": str(fruite.id), "name": "fruité", "color": "#c0392b", "category": gout_json},
        {"id": str(vanille.id), "name": "vanille", "color": "#f3e5ab", "category": odeur_json},
    ]


def test_list_tags_filtered_by_category(client: TestClient, session: Session) -> None:
    gout = create_tag_category(session, name="Goût")
    odeur = create_tag_category(session, name="Odeur")
    create_tag(session, gout, name="fruité")
    vanille = create_tag(session, odeur, name="vanille")

    response = client.get(URL, params={"category_id": str(odeur.id)})

    assert response.status_code == 200
    assert [tag["id"] for tag in response.json()] == [str(vanille.id)]


def test_list_tags_filtered_by_unknown_category_returns_empty_list(client: TestClient, session: Session) -> None:
    create_tag(session, create_tag_category(session))

    response = client.get(URL, params={"category_id": str(uuid4())})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tags_filtered_by_non_uuid_category_returns_400(client: TestClient) -> None:
    response = client.get(URL, params={"category_id": "abc"})

    assert response.status_code == 400
    assert response.json()["details"][0]["loc"] == ["query", "category_id"]


def test_list_tags_does_not_return_bottles(client: TestClient, session: Session) -> None:
    tag = create_tag(session, create_tag_category(session))
    tag_bottle(session, create_bottle(session), tag)

    response = client.get(URL)

    assert "bottles" not in response.json()[0]
