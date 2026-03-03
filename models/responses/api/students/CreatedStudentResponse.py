
from uuid import UUID

from pydantic import BaseModel


class CreatedStudentResponse(BaseModel):
    id: UUID
    username: str
    