
from uuid import UUID

from pydantic import BaseModel


class ResetOperatorPasswordResponse(BaseModel):
    id: UUID
    username: str
    password: str
    organisation_id: UUID
    