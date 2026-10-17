frontend en react

## Lancement

Le backend doit tourner sur http://127.0.0.1:9090 (voir `backend/README.md`). Depuis `frontend/` :

```bash
npm install
npm run dev        # http://localhost:5173, rechargement automatique
```

En développement, Vite redirige `/api/*` vers le backend (`vite.config.ts`), il n'y a donc pas de CORS à gérer.
Pour un backend ailleurs : `PINARD_BACKEND_URL=http://autre-hote:9090 npm run dev`.

```bash
npm run typecheck  # vérification TypeScript
npm run build      # build de production dans dist/
```

## Stack

- [React](https://react.dev) + TypeScript, construit avec [Vite](https://vite.dev)
- [Ant Design](https://ant.design) pour les composants (tableaux, modales, formulaires…), en français (`fr_FR`)
- [TanStack Query](https://tanstack.com/query) pour les appels à l'API : cache, chargement, et rechargement des listes
  après chaque création / modification / suppression
- [React Router](https://reactrouter.com) : une URL par section (`/bottles`, `/shelves`, `/tags`)

## Organisation

```
src/
├── main.tsx              # providers : thème antd, locale, React Query, routeur
├── App.tsx               # menu du haut + routes
├── api/                  # accès au backend
│   ├── client.ts         #   fetch + ApiError (message fonctionnel renvoyé par le backend)
│   ├── types.ts          #   types des ressources de l'API
│   └── bottles.ts, …     #   hooks React Query par ressource (lecture + mutations)
├── components/           # composants partagés
│   ├── FormModal.tsx     #   modale de création / édition (formulaire antd)
│   ├── TagBadge.tsx      #   étiquette colorée (texte noir ou blanc selon la couleur)
│   ├── TagSelect.tsx     #   sélection d'étiquettes groupées par catégorie
│   └── ShelfGrid.tsx     #   grille d'une étagère (cases libres cliquables)
├── features/             # une page par section, avec ses modales
│   ├── bottles/
│   ├── shelves/
│   └── tags/
└── hooks/useFeedback.ts  # messages de succès / d'erreur
```

Conventions :

- Les listes sont des `Table` antd, les créations / éditions des modales (`FormModal`).
- Chaque mutation invalide les requêtes des ressources impactées (ex : ranger une bouteille recharge les bouteilles
  et les étagères), voir les hooks de `src/api/`.
- Les erreurs de l'API (`{"code", "message"}`) sont affichées telles quelles via `useFeedback().error`.
