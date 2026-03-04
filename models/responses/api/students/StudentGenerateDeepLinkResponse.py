
from pydantic import BaseModel


class StudentGenerateDeepLinkResponse(BaseModel):
    deep_link: str