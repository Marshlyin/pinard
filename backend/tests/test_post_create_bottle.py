from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.infrastructure.entity import BottleEntity
from tests.factories import create_bottle, create_tag, create_tag_category

URL = "/bottles"


def test_create_bottle_returns_201(client: TestClient, session: Session) -> None:
    response = client.post(URL, json={"cuvee": "Les Picasses", "domain": "Olga Raffault", "vintage": 2020})

    assert response.status_code == 201
    body = response.json()
    assert body == {
        "id": body["id"],
        "cuvee": "Les Picasses",
        "domain": "Olga Raffault",
        "vintage": 2020,
        "quantity": 0,
        "tags": [],
    }
    entity = session.get(BottleEntity, UUID(body["id"]))
    assert entity is not None
    assert (entity.cuvee, entity.domain, entity.vintage) == ("Les Picasses", "Olga Raffault", 2020)


def test_create_bottle_without_vintage_returns_201(client: TestClient) -> None:
    response = client.post(URL, json={"cuvee": "Brut Réserve", "domain": "Billecart-Salmon"})

    assert response.status_code == 201
    assert response.json()["vintage"] is None


def test_create_bottle_strips_texts(client: TestClient) -> None:
    response = client.post(URL, json={"cuvee": "  Les Picasses ", "domain": " Olga Raffault  ", "vintage": 2020})

    assert response.status_code == 201
    assert (response.json()["cuvee"], response.json()["domain"]) == ("Les Picasses", "Olga Raffault")


def test_create_bottle_with_tags_returns_them_sorted_by_category_then_name(
    client: TestClient, session: Session
) -> None:
    type_ = create_tag_category(session, name="Type")
    gout = create_tag_category(session, name="Goût")
    rouge = create_tag(session, type_, name="rouge", color="#8e1b3a")
    fruite = create_tag(session, gout, name="fruité")
    boise = create_tag(session, gout, name="boisé")

    response = client.post(
        URL,
        json={
            "cuvee": "Les Picasses",
            "domain": "Olga Raffault",
            "tag_ids": [str(rouge.id), str(fruite.id), str(boise.id), str(rouge.id)],  # doublon ignoré
        },
    )

    assert response.status_code == 201
    assert [(tag["category"]["name"], tag["name"]) for tag in response.json()["tags"]] == [
        ("Goût", "boisé"),
        ("Goût", "fruité"),
        ("Type", "rouge"),
    ]
    assert response.json()["tags"][2] == {
        "id": str(rouge.id),
        "name": "rouge",
        "color": "#8e1b3a",
        "category": {"id": str(type_.id), "name": "Type"},
    }


def test_create_bottle_with_unknown_tags_returns_422(client: TestClient, session: Session) -> None:
    rouge = create_tag(session, create_tag_category(session), name="rouge")
    unknown_1, unknown_2 = uuid4(), uuid4()

    response = client.post(
        URL,
        json={
            "cuvee": "Les Picasses",
            "domain": "Olga Raffault",
            "tag_ids": [str(unknown_1), str(rouge.id), str(unknown_2)],
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "UNKNOWN_TAGS",
        "message": f"Étiquette(s) inexistante(s) : {unknown_1}, {unknown_2}",
    }
    assert session.exec(select(BottleEntity)).all() == []


@pytest.mark.parametrize(
    ("cuvee", "domain", "vintage"),
    [
        ("Les Picasses", "Olga Raffault", 2020),
        ("les picasses", "OLGA RAFFAULT", 2020),
        ("  Les Picasses ", "Olga Raffault", 2020),
    ],
)
def test_create_bottle_already_existing_returns_422(
    client: TestClient, session: Session, cuvee: str, domain: str, vintage: int
) -> None:
    create_bottle(session, cuvee="Les Picasses", domain="Olga Raffault", vintage=2020)

    response = client.post(URL, json={"cuvee": cuvee, "domain": domain, "vintage": vintage})

    assert response.status_code == 422
    assert response.json()["code"] == "BOTTLE_ALREADY_EXISTS"
    assert len(session.exec(select(BottleEntity)).all()) == 1


def test_create_bottle_already_existing_without_vintage_returns_422(client: TestClient, session: Session) -> None:
    create_bottle(session, cuvee="Brut Réserve", domain="Billecart-Salmon", vintage=None)

    response = client.post(URL, json={"cuvee": "Brut Réserve", "domain": "Billecart-Salmon"})

    assert response.status_code == 422
    assert response.json() == {
        "code": "BOTTLE_ALREADY_EXISTS",
        "message": "La bouteille 'Brut Réserve' du domaine 'Billecart-Salmon' (sans millésime) existe déjà",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"cuvee": "Les Picasses", "domain": "Olga Raffault", "vintage": 2019},  # autre millésime
        {"cuvee": "Les Picasses", "domain": "Olga Raffault", "vintage": None},  # sans millésime
        {"cuvee": "Les Picasses", "domain": "Charles Joguet", "vintage": 2020},  # autre domaine
        {"cuvee": "Les Barnabés", "domain": "Olga Raffault", "vintage": 2020},  # autre cuvée
    ],
)
def test_create_bottle_differing_by_one_field_returns_201(client: TestClient, session: Session, payload: dict) -> None:
    create_bottle(session, cuvee="Les Picasses", domain="Olga Raffault", vintage=2020)

    response = client.post(URL, json=payload)

    assert response.status_code == 201


@pytest.mark.parametrize(
    ("payload", "invalid_field"),
    [
        ({"domain": "Olga Raffault"}, "cuvee"),
        ({"cuvee": "Les Picasses"}, "domain"),
        ({"cuvee": "   ", "domain": "Olga Raffault"}, "cuvee"),
        ({"cuvee": "x" * 101, "domain": "Olga Raffault"}, "cuvee"),
        ({"cuvee": "Les Picasses", "domain": ""}, "domain"),
        ({"cuvee": "Les Picasses", "domain": "Olga Raffault", "vintage": 1799}, "vintage"),
        ({"cuvee": "Les Picasses", "domain": "Olga Raffault", "vintage": 2101}, "vintage"),
        ({"cuvee": "Les Picasses", "domain": "Olga Raffault", "vintage": "vieux"}, "vintage"),
        ({"cuvee": "Les Picasses", "domain": "Olga Raffault", "tag_ids": "rouge"}, "tag_ids"),
    ],
)
def test_create_bottle_with_invalid_parameters_returns_400(
    client: TestClient, session: Session, payload: dict, invalid_field: str
) -> None:
    response = client.post(URL, json=payload)

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PARAMETERS"
    assert [error["loc"] for error in response.json()["details"]] == [["body", invalid_field]]
    assert session.exec(select(BottleEntity)).all() == []


def test_create_bottle_with_non_uuid_tag_id_returns_400(client: TestClient) -> None:
    response = client.post(URL, json={"cuvee": "Les Picasses", "domain": "Olga Raffault", "tag_ids": ["abc"]})

    assert response.status_code == 400
    assert response.json()["details"][0]["loc"] == ["body", "tag_ids", 0]
