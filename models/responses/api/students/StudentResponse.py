
from uuid import UUID
from pydantic import BaseModel


class StudentResponse(BaseModel):
    id: UUID
    username: str