
from uuid import UUID
from pydantic import BaseModel


class GenerateDeepLinkRequest(BaseModel):
    student_id: UUID