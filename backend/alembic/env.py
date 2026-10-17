from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# Import nécessaire pour enregistrer les tables dans SQLModel.metadata
import src.infrastructure.entity  # noqa: F401
from alembic import context
from src.configuration.settings import Settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# L'URL vient des settings de l'application (surchargeable via PINARD_DATABASE_URL)
config.set_main_option("sqlalchemy.url", Settings().database_url)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (génère le SQL sans connexion)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite ne supporte qu'un ALTER TABLE très limité : le mode batch recrée la table si nécessaire
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
