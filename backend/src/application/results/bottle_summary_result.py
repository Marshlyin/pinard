from uuid import UUID

from pydantic import BaseModel


class BottleSummaryResult(BaseModel):
    """Format minimal d'une bouteille."""

    id: UUID
    cuvee: str
    domain: str
    vintage: int | None
