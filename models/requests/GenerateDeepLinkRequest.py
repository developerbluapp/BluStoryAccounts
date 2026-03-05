
from uuid import UUID
from pydantic import BaseModel


class GenerateDeepLinkRequest(BaseModel):
    member_id: UUID