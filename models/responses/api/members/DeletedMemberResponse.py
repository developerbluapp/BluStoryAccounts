from pydantic import BaseModel
from uuid import UUID
class DeletedMemberResponse(BaseModel):
    id: UUID
    username: str
    message: str
