from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.factories import create_bottle, create_shelf, create_tag, create_tag_category, place_bottle, tag_bottle

URL = "/bottles"


@pytest.fixture
def cellar(session: Session) -> dict[str, UUID]:
    """
    Cave de test pour les filtres. Renvoie les identifiants des étiquettes et des bouteilles, par nom.

    | Bouteille      | Type  | Garde        |
    |----------------|-------|--------------|
    | Chinon         | rouge | longue garde |
    | Gamay          | rouge | à boire vite |
    | Sancerre       | blanc | à boire vite |
    | Vouvray        | blanc | longue garde |
    | Sans étiquette | -     | -            |
    """
    type_ = create_tag_category(session, name="Type")
    garde = create_tag_category(session, name="Garde")
    tags = {
        "rouge": create_tag(session, type_, name="rouge"),
        "blanc": create_tag(session, type_, name="blanc"),
        "longue garde": create_tag(session, garde, name="longue garde"),
        "à boire vite": create_tag(session, garde, name="à boire vite"),
    }
    bottles = {
        "Chinon": ["rouge", "longue garde"],
        "Gamay": ["rouge", "à boire vite"],
        "Sancerre": ["blanc", "à boire vite"],
        "Vouvray": ["blanc", "longue garde"],
        "Sans étiquette": [],
    }
    ids = {name: tag.id for name, tag in tags.items()}
    for cuvee, tag_names in bottles.items():
        bottle = create_bottle(session, cuvee=cuvee, domain="Domaine")
        ids[cuvee] = bottle.id
        for tag_name in tag_names:
            tag_bottle(session, bottle, tags[tag_name])
    return ids


def test_list_bottles_without_bottle_returns_empty_list(client: TestClient) -> None:
    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() == []


def test_list_bottles_sorted_by_domain_cuvee_then_vintage(client: TestClient, session: Session) -> None:
    raffault_2020 = create_bottle(session, cuvee="Les Picasses", domain="Olga Raffault", vintage=2020)
    joguet = create_bottle(session, cuvee="Les Varennes", domain="Charles Joguet", vintage=2019)
    raffault_2018 = create_bottle(session, cuvee="Les Picasses", domain="Olga Raffault", vintage=2018)
    barnabes = create_bottle(session, cuvee="les Barnabés", domain="olga raffault", vintage=2021)

    response = client.get(URL)

    assert response.status_code == 200
    assert [bottle["id"] for bottle in response.json()] == [
        str(joguet.id),
        str(barnabes.id),
        str(raffault_2018.id),
        str(raffault_2020.id),
    ]


def test_list_bottles_returns_quantity_and_tags(client: TestClient, session: Session) -> None:
    category = create_tag_category(session, name="Type")
    rouge = create_tag(session, category, name="rouge", color="#8e1b3a")
    shelf = create_shelf(session)
    bottle = create_bottle(session, cuvee="Les Picasses", domain="Olga Raffault", vintage=2020)
    tag_bottle(session, bottle, rouge)
    place_bottle(session, bottle, shelf, row=1, column=1)
    place_bottle(session, bottle, shelf, row=1, column=2)
    empty = create_bottle(session, cuvee="Bue", domain="Domaine vide", vintage=None)

    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(empty.id),
            "cuvee": "Bue",
            "domain": "Domaine vide",
            "vintage": None,
            "quantity": 0,
            "tags": [],
        },
        {
            "id": str(bottle.id),
            "cuvee": "Les Picasses",
            "domain": "Olga Raffault",
            "vintage": 2020,
            "quantity": 2,
            "tags": [
                {
                    "id": str(rouge.id),
                    "name": "rouge",
                    "color": "#8e1b3a",
                    "category": {"id": str(category.id), "name": "Type"},
                }
            ],
        },
    ]


def test_list_bottles_does_not_return_placements(client: TestClient, session: Session) -> None:
    place_bottle(session, create_bottle(session), create_shelf(session), row=1, column=1)

    response = client.get(URL)

    assert "placements" not in response.json()[0]


def cuvees(client: TestClient, tag_ids: list[UUID | str]) -> list[str]:
    response = client.get(URL, params={"tag_id": [str(tag_id) for tag_id in tag_ids]})
    assert response.status_code == 200
    return [bottle["cuvee"] for bottle in response.json()]


@pytest.mark.parametrize(
    ("tag_names", "expected_cuvees"),
    [
        (["rouge"], ["Chinon", "Gamay"]),
        (["longue garde"], ["Chinon", "Vouvray"]),
        # Même catégorie : OU
        (["rouge", "blanc"], ["Chinon", "Gamay", "Sancerre", "Vouvray"]),
        # Catégories différentes : ET
        (["rouge", "longue garde"], ["Chinon"]),
        (["blanc", "à boire vite"], ["Sancerre"]),
        # (rouge OU blanc) ET longue garde
        (["rouge", "blanc", "longue garde"], ["Chinon", "Vouvray"]),
        # (rouge OU blanc) ET (longue garde OU à boire vite)
        (["rouge", "blanc", "longue garde", "à boire vite"], ["Chinon", "Gamay", "Sancerre", "Vouvray"]),
    ],
)
def test_list_bottles_filtered_by_tags(
    client: TestClient, cellar: dict[str, UUID], tag_names: list[str], expected_cuvees: list[str]
) -> None:
    assert cuvees(client, [cellar[name] for name in tag_names]) == expected_cuvees


def test_list_bottles_filtered_returns_all_tags_of_matching_bottles(
    client: TestClient, cellar: dict[str, UUID]
) -> None:
    response = client.get(URL, params={"tag_id": str(cellar["longue garde"])})

    chinon = next(bottle for bottle in response.json() if bottle["cuvee"] == "Chinon")
    assert sorted(tag["name"] for tag in chinon["tags"]) == ["longue garde", "rouge"]


def test_list_bottles_filtered_with_duplicate_tag_ids(client: TestClient, cellar: dict[str, UUID]) -> None:
    assert cuvees(client, [cellar["rouge"], cellar["rouge"]]) == ["Chinon", "Gamay"]


def test_list_bottles_filtered_by_tag_without_bottle_returns_empty_list(
    client: TestClient, session: Session, cellar: dict[str, UUID]
) -> None:
    rose = create_tag(session, create_tag_category(session, name="Couleur"), name="rosé")

    assert cuvees(client, [rose.id]) == []


def test_list_bottles_filtered_by_unknown_tag_returns_empty_list(client: TestClient, cellar: dict[str, UUID]) -> None:
    assert cuvees(client, [uuid4()]) == []
    assert cuvees(client, [cellar["rouge"], uuid4()]) == []


def test_list_bottles_filtered_by_non_uuid_tag_returns_400(client: TestClient) -> None:
    response = client.get(URL, params={"tag_id": ["abc"]})

    assert response.status_code == 400
    assert response.json()["details"][0]["loc"] == ["query", "tag_id", 0]
