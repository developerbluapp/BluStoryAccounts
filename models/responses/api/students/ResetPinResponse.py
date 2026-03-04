
from uuid import UUID

from pydantic import BaseModel


class ResetPinResponse(BaseModel):
    student_id: UUID
    pin: str