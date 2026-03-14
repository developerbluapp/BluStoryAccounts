from typing import List

from pydantic import BaseModel
from uuid import UUID


class AuthenticatedMember(BaseModel):
    id :UUID
    operator_id: UUID
    email: str
    roles: List[str]
    aud: str
