from pydantic import BaseModel
from uuid import UUID
class StudentDeepLink(BaseModel):
    student_id: UUID
    deep_link: str