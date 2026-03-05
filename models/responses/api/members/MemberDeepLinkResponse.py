
from pydantic import BaseModel

from uuid import UUID
class MemberDeepLinkResponse(BaseModel):
    member_id: UUID
    deep_link: str