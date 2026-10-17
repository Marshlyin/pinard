from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope


class SpaStaticFiles(StaticFiles):
    """
    Fichiers statiques d'une single page application : un chemin sans fichier correspondant (ex : /bottles, géré par
    le routeur du front) renvoie index.html au lieu d'une 404, pour qu'un rafraîchissement de page fonctionne.
    """

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            response = await super().get_response(path, scope)
        except HTTPException as exception:
            if exception.status_code != 404:
                raise
            return await super().get_response("index.html", scope)

        if response.status_code == 404:
            return await super().get_response("index.html", scope)
        return response
