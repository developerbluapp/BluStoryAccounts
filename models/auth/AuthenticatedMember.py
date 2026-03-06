from typing import List

from pydantic import BaseModel
from uuid import UUID


class AuthenticatedMember(BaseModel):
    id :UUID
    license_holder_id: UUID
    email: str
    roles: List[str]
    aud: str
