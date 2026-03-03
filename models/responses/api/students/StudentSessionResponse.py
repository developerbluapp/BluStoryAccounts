
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.students.StudentResponse import StudentResponse
class StudentSessionResponse(BaseModel):
    student: StudentResponse
    session: Session