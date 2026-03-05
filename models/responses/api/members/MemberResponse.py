
from uuid import UUID
from pydantic import BaseModel


class MemberResponse(BaseModel):
    id: UUID
    username: str
    first_name:str