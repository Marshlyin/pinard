def is_same_name(first: str, second: str) -> bool:
    """Deux noms sont identiques sans tenir compte de la casse (« Fruité » et « fruité » sont le même nom)."""
    return first.casefold() == second.casefold()
