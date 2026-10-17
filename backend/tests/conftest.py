from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from injector import Binder, Injector, Module, singleton
from sqlalchemy import Engine, event
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import src.infrastructure.entity  # noqa: F401  (enregistre les tables dans SQLModel.metadata)
from src.app import create_app
from src.configuration import injection_helper
from src.configuration.module import ConfigurationModule


@pytest.fixture
def engine() -> Generator[Engine]:
    # Base SQLite en mémoire, recréée pour chaque test. StaticPool : une seule connexion partagée, sinon chaque
    # connexion verrait une base vide
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:  # noqa: ANN001
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Generator[Session]:
    with Session(engine) as session:
        yield session


@pytest.fixture
def test_injector(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> Injector:
    """Injector neuf par test (singletons non partagés), dont l'Engine pointe vers la base de test."""

    class TestModule(Module):
        def configure(self, binder: Binder) -> None:
            binder.bind(Engine, to=engine, scope=singleton)

    # Les bindings du dernier module écrasent ceux de ConfigurationModule
    test_injector = Injector([ConfigurationModule(), TestModule()])
    monkeypatch.setattr(injection_helper, "injector_get_bound_type", test_injector.get)
    return test_injector


@pytest.fixture
def client(test_injector: Injector) -> Generator[TestClient]:
    with TestClient(create_app()) as client:
        yield client
