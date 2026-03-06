from typing import List

from pydantic import BaseModel
from uuid import UUID


class AuthenticatedOperator(BaseModel):
    id :UUID
    email: str
    roles: List[str]
    aud: str
