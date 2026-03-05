
from uuid import UUID

from pydantic import BaseModel


class ResetPinResponse(BaseModel):
    member_id: UUID
    pin: str