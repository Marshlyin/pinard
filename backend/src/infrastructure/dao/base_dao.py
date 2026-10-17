from collections.abc import Iterator
from contextlib import contextmanager

from injector import inject
from sqlalchemy import Engine
from sqlmodel import Session


class BaseDAO:
    """
    Fournit une session courte par opération. Les repositories sont des singletons partagés entre les threads de
    FastAPI : ils ne doivent pas garder de session, ils en ouvrent une à chaque appel via `session()`.
    """

    @inject
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    @contextmanager
    def session(self) -> Iterator[Session]:
        # expire_on_commit=False : les entités restent lisibles après le commit, sans requête de rechargement
        with Session(self.engine, expire_on_commit=False) as session:
            yield session
