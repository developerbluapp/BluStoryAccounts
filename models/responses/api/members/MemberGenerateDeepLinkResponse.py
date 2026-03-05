
from pydantic import BaseModel


class MemberGenerateDeepLinkResponse(BaseModel):
    deep_link: str