"""Application de production : API sous /api, front compilé à la racine (avec retour sur index.html)."""

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from injector import Injector

from src.app import create_production_app

INDEX_HTML = "<!doctype html><title>Pinard</title>"


@pytest.fixture
def frontend_dist_dir(tmp_path: Path) -> Path:
    """Faux résultat de `npm run build`."""
    (tmp_path / "index.html").write_text(INDEX_HTML)
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "index-abc123.js").write_text("console.log('pinard')")
    return tmp_path


@pytest.fixture
def production_client(
    test_injector: Injector, frontend_dist_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[TestClient]:
    monkeypatch.setenv("PINARD_FRONTEND_DIST_DIR", str(frontend_dist_dir))
    with TestClient(create_production_app()) as client:
        yield client


def test_api_is_served_under_api_prefix(production_client: TestClient) -> None:
    created = production_client.post("/api/shelves", json={"name": "Cave", "rows": 3, "columns": 4})

    assert created.status_code == 201
    assert [shelf["name"] for shelf in production_client.get("/api/shelves").json()] == ["Cave"]


def test_api_errors_keep_their_format(production_client: TestClient) -> None:
    response = production_client.get("/api/shelves/abc")

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PARAMETERS"


def test_api_documentation_is_served_under_api_prefix(production_client: TestClient) -> None:
    assert production_client.get("/api/docs").status_code == 200
    assert production_client.get("/api/openapi.json").json()["paths"].keys() >= {"/shelves", "/bottles", "/tags"}


def test_frontend_index_is_served_at_root(production_client: TestClient) -> None:
    response = production_client.get("/")

    assert response.status_code == 200
    assert response.text == INDEX_HTML


def test_frontend_assets_are_served(production_client: TestClient) -> None:
    response = production_client.get("/assets/index-abc123.js")

    assert response.status_code == 200
    assert response.text == "console.log('pinard')"


@pytest.mark.parametrize("front_route", ["/bottles", "/shelves", "/tags", "/une/route/inconnue"])
def test_frontend_routes_fall_back_to_index(production_client: TestClient, front_route: str) -> None:
    # Rafraîchissement de page sur une route du routeur React : pas de fichier, on renvoie l'application
    response = production_client.get(front_route)

    assert response.status_code == 200
    assert response.text == INDEX_HTML


def test_root_api_paths_are_not_exposed(production_client: TestClient) -> None:
    # Sans le préfixe /api, /shelves est une route du front et non l'API
    response = production_client.get("/shelves")

    assert response.text == INDEX_HTML


def test_production_app_requires_frontend_dist_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PINARD_FRONTEND_DIST_DIR", str(tmp_path))  # dossier sans index.html

    with pytest.raises(RuntimeError, match="Front compilé introuvable"):
        create_production_app()
