from typing import List

from pydantic import BaseModel
from uuid import UUID


class AuthenticatedAdmin(BaseModel):
    id: UUID
    organisation_id: UUID
    email: str
    roles: List[str]
    aud: str
