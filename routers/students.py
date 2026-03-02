# routers/users.py
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends

from dependencies import get_user_service
from models.requests import CreateUserRequest,UpdateStudentRequest
from models.responses import CreatedStudentResponse
from services import UserService
from models.responses import StudentResponse
UserServiceDep = Annotated[UserService, Depends(get_user_service)]

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/{license_holder_id}", response_model=CreatedStudentResponse, status_code=201)
def create_student(license_holder_id: UUID, body: CreateUserRequest, service: UserServiceDep):
    student = service.register_student(body.username, body.password, license_holder_id=str(license_holder_id))
    return CreatedStudentResponse(id=student.id, username=student.username)

@router.get("/{license_holder_id}/students", response_model=list[StudentResponse])
def get_students(license_holder_id: UUID, service: UserServiceDep):
    students = service.get_students_by_license_holder(license_holder_id)
    return [StudentResponse(id=s.id, username=s.username) for s in students]


@router.get("/{license_holder_id}/students/{student_id}", response_model=StudentResponse)
def get_student(license_holder_id: UUID, student_id: UUID, service: UserServiceDep):

    student = service.get_student_by_id(license_holder_id, student_id)
    if not student:
        raise AppException(code="student_not_found", message="Student not found", status=404)
    return StudentResponse(id=student.id, username=student.username)

    
@router.delete("/{license_holder_id}/students/{student_id}")
def delete_student(license_holder_id: UUID,student_id: UUID,service: UserServiceDep):
    delete_student = service.delete_student_by_id(license_holder_id, student_id)
    return {"detail": f"Student with id {delete_student.id} deleted successfully."}

@router.patch("/{license_holder_id}/students/{student_id}")
def update_student(license_holder_id: UUID, student_id: UUID, body: UpdateStudentRequest, service: UserServiceDep):
    # Example of a patch operation - in a real app, this would update student details
    student = service.update_student_by_id(license_holder_id, student_id, body.username)
    return {"detail": f"Student with id {student_id} updated successfully."}