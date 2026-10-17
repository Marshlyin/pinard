backend en fast api

## Lancement

Toutes les commandes se lancent depuis `backend/` :

```bash
uv sync                      # installe les dépendances
uv run alembic upgrade head  # crée / met à jour la base
uv run python local.py       # lance l'API sur http://127.0.0.1:9090 (rechargement automatique)
```

Documentation interactive de l'API : http://127.0.0.1:9090/docs

Deux points d'entrée dans `src/app.py` :

- `create_app()` : l'API seule, routes à la racine (`/shelves`…). Utilisée par `local.py` et les tests ; en
  développement, le front est servi par Vite, qui redirige `/api/*` vers cette API.
- `create_production_app()` : l'API montée sous `/api` (documentation sur `/api/docs`) et le front compilé à la
  racine, avec retour sur `index.html` pour les routes du front (`SpaStaticFiles`). Lancée par `prod.py` dans l'image
  Docker, elle nécessite `PINARD_FRONTEND_DIST_DIR` (voir le [README racine](../README.md) pour le déploiement).

## API

| Ressource | Endpoints | Règles principales |
|---|---|---|
| Étagères | `POST/GET /shelves`, `GET/PUT/DELETE /shelves/{id}` | nom unique ; pas de réduction qui laisserait des bouteilles hors grille ; suppression uniquement si vide |
| Catégories d'étiquettes | `POST/GET /tag-categories`, `GET/PUT/DELETE /tag-categories/{id}` | nom unique ; suppression uniquement si vide |
| Étiquettes | `POST/GET /tags` (`?category_id=`), `GET/PUT/DELETE /tags/{id}` | nom unique dans sa catégorie ; couleur `#rrggbb` (gris `#9e9e9e` par défaut, obligatoire au PUT) ; la suppression retire l'étiquette des bouteilles |
| Bouteilles | `POST/GET /bottles` (`?tag_id=` répétable : OU dans une catégorie, ET entre catégories), `GET/PUT/DELETE /bottles/{id}` | domaine + cuvée + millésime unique ; étiquettes via `tag_ids` (remplacées par le PUT) ; la suppression retire aussi les emplacements |
| Emplacements | `POST /bottles/{id}/placements`, `PUT/DELETE /bottles/{id}/placements/{placement_id}` | une bouteille physique par case ; la case doit exister dans l'étagère |

Une bouteille en base est une référence de vin : sa `quantity` est le nombre d'emplacements occupés (une bouteille
physique par emplacement).

## Architecture

Découpage Domain Driven Design : chaque endpoint traverse les trois couches, et le domaine ne dépend jamais de
l'application ni de l'infrastructure.

```
src/
├── app.py                  # création de l'app FastAPI (routers + gestionnaires d'erreurs)
├── application/            # couche HTTP
│   ├── routers/            #   endpoints (un router par ressource)
│   ├── commands/           #   corps des requêtes (Pydantic) : validation du format
│   ├── results/            #   corps des réponses (Pydantic)
│   ├── mappers/            #   commande → domaine, domaine → résultat (fonctions)
│   └── exception_handlers.py  # erreurs du domaine / de validation → réponses HTTP
├── domain/                 # cœur métier, sans dépendance à FastAPI ni à la base
│   ├── model/              #   objets métier (dataclasses)
│   ├── services/           #   règles métier
│   ├── repositories/       #   interfaces (ABC) des repositories
│   └── exceptions/         #   erreurs métier et leurs codes (BusinessErrorCode)
├── infrastructure/         # accès aux données
│   ├── entity/             #   tables SQLModel
│   ├── repositories/       #   implémentations des interfaces du domaine
│   ├── mappers/            #   entité ↔ domaine (classes injectées)
│   ├── dao/base_dao.py     #   fournit une session SQL courte par opération
│   └── database.py         #   construction de l'Engine
└── configuration/
    ├── module.py           # déclaration de toutes les dépendances (injector)
    ├── injection_helper.py # injects() : branche injector sur les Depends de FastAPI
    ├── settings.py         # configuration (variables d'environnement PINARD_*)
    └── logging.py
```

### Injection de dépendances

Les dépendances sont gérées par la librairie [`injector`](https://injector.readthedocs.io/). Tous les bindings sont
déclarés dans `src/configuration/module.py`, en singletons :

```python
binder.bind(ShelfRepository, to=ShelfRepositoryImpl, scope=singleton)  # interface du domaine → implémentation
binder.bind(ShelvesService, scope=singleton)
```

Les constructeurs déclarent leurs dépendances avec `@inject`. Dans les routers, un service s'injecte avec `injects` :

```python
def get_shelf(
    id: Annotated[UUID, Path(title="L'identifiant de l'étagère")],
    shelves_service: ShelvesService = injects(ShelvesService),  # noqa: B008
) -> ShelfDetailResult:
```

Les repositories étant des singletons partagés entre les threads de FastAPI, ils ne gardent **jamais** de session SQL.
Chaque méthode en ouvre une via le `BaseDAO` :

```python
with self.base_dao.session() as session:
    ...
```

### Conventions

- **Identifiants** : tous les `id` (clés primaires, clés étrangères, paramètres de chemin) sont des UUID v4. Le domaine
  génère l'identifiant à la création de l'objet (`id: UUID = field(default_factory=uuid4)`).
- **Codes HTTP** :

  | Code | Cas | Origine |
  |---|---|---|
  | 400 | paramètres invalides (format, champ manquant, id non UUID) | validation Pydantic |
  | 404 | ressource introuvable | `ResourceNotFoundError` du domaine |
  | 422 | règle métier non respectée | `DomainError` du domaine |

  Les erreurs ont toutes le format `{"code": "...", "message": "..."}` (plus `details` pour les 400).
- **Unicité des noms** (étagères, catégories d'étiquettes, étiquettes) : vérifiée par le domaine sans tenir compte de
  la casse, avec `is_same_name` (`domain/model/names.py`). « Cave » et « cave » sont le même nom, mais pas « Étagère »
  et « Etagere ». Les espaces autour du nom sont retirés par les commandes.
- **Langue** : noms de code en anglais, commentaires, logs et messages d'erreur en français.

### Ajouter un endpoint

1. **Domaine** : modèle dans `model/`, méthode dans le service (avec les règles métier), méthode abstraite dans
   l'interface du repository, et si besoin une nouvelle erreur dans `exceptions/` avec son code dans `BusinessErrorCode`.
2. **Infrastructure** : implémentation dans le repository (`with self.base_dao.session()`), mapper entité ↔ domaine.
3. **Application** : commande et/ou résultat, mapper, route dans le router. Un nouveau router se déclare avec
   `responses=DEFAULT_RESPONSES` (`src/transverse/application_constants.py`) et s'enregistre dans `src/app.py`.
4. **Configuration** : binder dans `module.py` tout nouveau service, repository ou mapper.
5. **Tests** : un fichier `tests/test_<verbe>_<fonction_du_endpoint>.py`.

## Tests

```bash
uv run pytest
```

Un fichier par endpoint dans `tests/`, nommé `test_<verbe>_<fonction_du_endpoint>.py` (ex : `test_post_create_shelf.py`).

- Chaque test tourne sur une base SQLite en mémoire neuve, la base locale n'est jamais touchée.
- Chaque test reçoit un injector neuf, dont l'`Engine` pointe vers cette base. Aucun singleton n'est partagé entre deux
  tests (voir les fixtures de `tests/conftest.py`).
- Fixtures disponibles : `client` (appels HTTP) et `session` (vérifications directes en base).
- `tests/factories.py` permet d'insérer directement des données en base (étagères, bouteilles, emplacements).

## Base de données

SQLite par défaut (`backend/pinard.db`), surchargeable via la variable `PINARD_DATABASE_URL` (ou un fichier `backend/.env`).
Le schéma est versionné avec alembic, à partir des entités SQLModel de `src/infrastructure/entity/`.

```bash
uv run alembic upgrade head                              # crée / met à jour la base
uv run alembic revision --autogenerate -m "description"  # génère une migration après modification d'une entité
uv run alembic downgrade -1                              # annule la dernière migration
uv run alembic check                                     # vérifie que les entités et les migrations sont synchronisées
```

Points d'attention :

- Une nouvelle entité doit être importée dans `src/infrastructure/entity/__init__.py`, sinon alembic ne la détecte pas.
- Toujours relire une migration générée. Un **renommage** de colonne est vu par l'autogenerate comme une suppression
  suivie d'un ajout, ce qui efface les données : il faut le réécrire avec `batch_op.alter_column(..., new_column_name=...)`.
- SQLite ne supporte qu'un `ALTER TABLE` limité, alembic recrée donc la table (mode batch). Un index sur une colonne
  renommée doit être créé **après** le bloc `batch_alter_table`, avec `op.create_index`.
- Ajouter une colonne `NOT NULL` à une table qui contient déjà des lignes nécessite un `server_default` temporaire.
