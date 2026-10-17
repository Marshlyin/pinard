# Pinard

Gestionnaire de collection pour cave à vin

- `backend/` : API FastAPI + SQLite (voir [backend/README.md](backend/README.md))
- `frontend/` : interface React + Ant Design (voir [frontend/README.md](frontend/README.md))

## Développement

```bash
cd backend && uv run python local.py      # API sur http://127.0.0.1:9090
cd frontend && npm install && npm run dev  # interface sur http://localhost:5173
```

## Production (Docker Compose)

Un seul conteneur : FastAPI sert l'API sous `/api` et l'interface compilée à la racine. Pas de nginx nécessaire.
La base SQLite est stockée dans le volume Docker `pinard-data`, conservé aux redémarrages et mises à jour.

```bash
docker compose up -d --build   # construit l'image et démarre : http://<serveur>:2020
```

- Le port se change avec la variable `PINARD_PORT` (ex : `PINARD_PORT=9000 docker compose up -d`, ou dans un
  fichier `.env` à côté de `docker-compose.yml`).
- Les migrations de la base sont appliquées automatiquement à chaque démarrage du conteneur.
- La documentation de l'API est sur `http://<serveur>:2020/api/docs`.

### Commandes utiles

```bash
docker compose logs -f                # logs de l'application
docker compose ps                     # état du conteneur (healthy une fois démarré)
git pull && docker compose up -d --build   # mise à jour : nouvelle image, la base est conservée
docker compose down                   # arrêt (la base est conservée)
```

⚠️ `docker compose down -v` **supprime le volume, donc la base**.

### Sauvegarde et restauration de la base

```bash
# Sauvegarde : copie de pinard.db dans le dossier courant (application arrêtée pour une copie cohérente)
docker compose stop
docker run --rm -v pinard-data:/data -v "$PWD":/backup alpine cp /data/pinard.db /backup/pinard-$(date +%F).db
docker compose start

# Restauration d'une sauvegarde
docker compose stop
docker run --rm -v pinard-data:/data -v "$PWD":/backup alpine sh -c \
  "cp /backup/pinard-AAAA-MM-JJ.db /data/pinard.db && chown 1000:1000 /data/pinard.db"
docker compose start
```

### HTTPS / accès depuis Internet

Le conteneur sert du HTTP simple, prévu pour un réseau local. Pour du HTTPS ou un accès depuis l'extérieur, placer un
reverse proxy (Caddy, Traefik, nginx…) au niveau du serveur, devant le port du conteneur.
