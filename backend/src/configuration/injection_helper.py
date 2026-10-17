from typing import Any

from fastapi import Depends

from src.configuration.module import injector


def injects[InjectionTargetType](bound_type: type[InjectionTargetType]) -> Any:
    """
    Obtenir une instance depuis injector pour l'injecter dans un Depends de fastapi sur une route.
    """

    def get_bound_type_instance() -> InjectionTargetType:
        return injector_get_bound_type(bound_type)

    # Retourne un Depends au moment de l'import.
    # La méthode cible ne serait appelée que lorsqu'on appelle le endpoint
    return Depends(get_bound_type_instance)


def injector_get_bound_type[InjectionTargetType](bound_type: type[InjectionTargetType]) -> InjectionTargetType:
    """
    Obtenir l'instance depuis l'injector. Mis dans une méthode à part pour permettre de mocker si besoin.
    """
    return injector.get(bound_type)
