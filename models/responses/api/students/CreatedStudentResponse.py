
from uuid import UUID

from pydantic import BaseModel

from blustorymicroservices.BluStoryLicenseHolders.models.dtos.Student import Student


class CreatedStudentResponse(BaseModel):
    student: Student
    deep_link: str


