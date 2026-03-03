# routers/users.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, HTTPException

from blustorymicroservices.BluStoryLicenseHolders.dependencies.services import get_student_auth_service
from models.requests import StudentSigninRequest
from models.responses import CreatedStudentResponse
from services import StudentAuthService
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.students.StudentSessionResponse import StudentSessionResponse
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.students.StudentResponse import StudentResponse
StudentAuthServiceDEP = Annotated[StudentAuthService, Depends(get_student_auth_service)]

router = APIRouter(prefix="/auth/student", tags=["auth-student"])

@router.post("/signin", response_model=StudentSessionResponse ,status_code=201)
def signin_student(body: StudentSigninRequest, student_service: StudentAuthServiceDEP):
    session_response= student_service.signin_student(body)
    return StudentSessionResponse(student=StudentResponse(id=session_response.student.id,username=session_response.student.username),session=session_response.session) 

