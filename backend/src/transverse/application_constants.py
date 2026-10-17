from typing import Any

# Réponses documentées (OpenAPI) communes à tous les routers
DEFAULT_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {"description": "OK"},
    201: {"description": "Creation de la ressource"},
    204: {"description": "Pas de contenu"},
    400: {"description": "Erreur sur les paramètres en entrée"},
    404: {"description": "Erreur resource non trouvée"},
    422: {"description": "Erreur fonctionnelle"},
    500: {"description": "Erreur interne"},
    502: {"description": "Erreur du service fournissant les données"},
}
