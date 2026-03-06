
from pydantic import BaseModel
from uuid import UUID
class OperatorResponse(BaseModel):
    id: UUID
    email: str
