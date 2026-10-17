from sqlalchemy import Engine, event
from sqlmodel import create_engine

from src.configuration.settings import Settings


def build_engine(settings: Settings) -> Engine:
    is_sqlite = settings.database_url.startswith("sqlite")
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        # SQLite interdit par défaut le partage d'une connexion entre threads (FastAPI exécute les routes sync
        # dans un threadpool)
        connect_args={"check_same_thread": False} if is_sqlite else {},
    )

    if is_sqlite:

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:  # noqa: ANN001
            # Les clés étrangères ne sont pas vérifiées par SQLite sans ce pragma
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine
