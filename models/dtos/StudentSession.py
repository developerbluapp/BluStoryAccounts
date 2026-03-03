
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.BluStoryLicenseHolders.models.dtos import Student
class StudentSession(BaseModel):
    student: Student
    session: Session