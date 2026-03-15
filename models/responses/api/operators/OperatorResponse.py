
from pydantic import BaseModel
from uuid import UUID
class OperatorResponse(BaseModel):
    id: UUID
    username: str
    email: str
