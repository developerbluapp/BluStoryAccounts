from uuid import UUID

from pydantic import BaseModel

class PatchedMemberResponse(BaseModel):
    id:UUID
    username: str
    message: str 