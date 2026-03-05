from typing import List

from pydantic import BaseModel
from uuid import UUID


class AuthenticatedLicenseHolder(BaseModel):
    id :UUID
    email: str
    roles: List[str]
    aud: str
