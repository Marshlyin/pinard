# syntax=docker/dockerfile:1

# --- Étape 1 : compilation du front (fichiers statiques dans /frontend/dist) ---
FROM node:24-slim AS frontend

WORKDIR /frontend
# Dépendances d'abord : la couche npm ci reste en cache tant que package*.json ne change pas
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


# --- Étape 2 : backend FastAPI, qui sert aussi le front compilé ---
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PINARD_DATABASE_URL=sqlite:////data/pinard.db \
    PINARD_FRONTEND_DIST_DIR=/app/frontend_dist

WORKDIR /app

# Dépendances d'abord (sans le code), pour profiter du cache Docker
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY backend/ ./
COPY --from=frontend /frontend/dist ./frontend_dist

# Utilisateur non root, propriétaire du dossier de la base (le volume nommé hérite de ces droits à sa création)
RUN useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin pinard \
    && mkdir /data \
    && chown pinard:pinard /data
USER pinard
VOLUME /data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/shelves')"

# Migrations de la base à chaque démarrage (sans effet si déjà à jour), puis lancement de l'application
CMD ["sh", "-c", "alembic upgrade head && exec python prod.py"]
