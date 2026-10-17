from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR: Path = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PINARD_", env_file=BACKEND_DIR / ".env", extra="ignore")

    database_url: str = f"sqlite:///{BACKEND_DIR / 'pinard.db'}"
    database_echo: bool = False

    # Front compilé (npm run build) servi par create_production_app. Inutile en développement (servi par Vite)
    frontend_dist_dir: Path | None = None
