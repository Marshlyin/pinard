from uuid import UUID

from pydantic import BaseModel


class TagCategoryResult(BaseModel):
    id: UUID
    name: str
