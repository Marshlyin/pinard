from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.factories import create_bottle, create_tag, create_tag_category, tag_bottle


def url(tag_id: UUID | str) -> str:
    return f"/tags/{tag_id}"


def test_get_tag_without_bottle_returns_empty_bottles(client: TestClient, session: Session) -> None:
    category = create_tag_category(session, name="Goût")
    tag = create_tag(session, category, name="fruité", color="#c0392b")

    response = client.get(url(tag.id))

    assert response.status_code == 200
    assert response.json() == {
        "id": str(tag.id),
        "name": "fruité",
        "color": "#c0392b",
        "category": {"id": str(category.id), "name": "Goût"},
        "bottles": [],
    }


def test_get_tag_returns_its_bottles_sorted_by_domain_cuvee_vintage(client: TestClient, session: Session) -> None:
    tag = create_tag(session, create_tag_category(session))
    raffault_2020 = create_bottle(session, cuvee="Les Picasses", domain="Olga Raffault", vintage=2020)
    raffault_2018 = create_bottle(session, cuvee="Les Picasses", domain="Olga Raffault", vintage=2018)
    billecart = create_bottle(session, cuvee="Brut Réserve", domain="Billecart-Salmon", vintage=None)
    untagged = create_bottle(session, cuvee="Autre", domain="Autre domaine")
    for bottle in (raffault_2020, billecart, raffault_2018):
        tag_bottle(session, bottle, tag)

    response = client.get(url(tag.id))

    assert response.status_code == 200
    assert [bottle["id"] for bottle in response.json()["bottles"]] == [
        str(billecart.id),
        str(raffault_2018.id),
        str(raffault_2020.id),
    ]
    assert str(untagged.id) not in {bottle["id"] for bottle in response.json()["bottles"]}
    assert response.json()["bottles"][0] == {
        "id": str(billecart.id),
        "cuvee": "Brut Réserve",
        "domain": "Billecart-Salmon",
        "vintage": None,
    }


def test_get_unknown_tag_returns_404(client: TestClient) -> None:
    unknown_id = uuid4()

    response = client.get(url(unknown_id))

    assert response.status_code == 404
    assert response.json() == {"code": "TAG_NOT_FOUND", "message": f"Aucune étiquette avec l'identifiant {unknown_id}"}


def test_get_tag_with_non_uuid_id_returns_400(client: TestClient) -> None:
    response = client.get(url("abc"))

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PARAMETERS"
