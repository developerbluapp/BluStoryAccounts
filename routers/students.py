from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.models.auth.AuthenticatedLicenseHolder import AuthenticatedLicenseHolder
from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.base import AppException
from fastapi import APIRouter, Depends

from dependencies import get_student_service, get_current_user
from models.requests import CreateUserRequest, UpdateStudentRequest
from models.responses import CreatedStudentResponse, StudentResponse,DeletedStudentResponse, PatchedStudentResponse
from services import StudentService


StudentServiceDEP = Annotated[StudentService, Depends(get_student_service)]
AuthenticatedUserDEP = Annotated[AuthenticatedLicenseHolder, Depends(get_current_user)]

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=CreatedStudentResponse, status_code=201)
def create_student(
    body: CreateUserRequest,
    student_service: StudentServiceDEP,
    current_user: AuthenticatedUserDEP,
):
    license_holder_id = str(current_user.id)

    student = student_service.register_student(
        body.username,
        body.password,
        license_holder_id=license_holder_id,
    )

    return CreatedStudentResponse(
        id=student.id,
        username=student.username,
    )


@router.get("", response_model=list[StudentResponse])
def get_students(
    student_service: StudentServiceDEP,
    current_user: AuthenticatedUserDEP,
):
    license_holder_id = current_user.id

    students = student_service.get_students_by_license_holder(license_holder_id)

    return [
        StudentResponse(id=s.id, username=s.username)
        for s in students
    ]


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: UUID,
    student_service: StudentServiceDEP,
    current_user: AuthenticatedUserDEP,
):
    license_holder_id = current_user.id

    student = student_service.get_student_by_id(
        license_holder_id,
        student_id,
    )

    if not student:
        raise AppException(
            code="student_not_found",
            message="Student not found",
            status=404,
        )

    return StudentResponse(
        id=student.id,
        username=student.username,
    )


@router.delete("/{student_id}")
def delete_student(
    student_id: UUID,
    student_service: StudentServiceDEP,
    current_user: AuthenticatedUserDEP,
):
    license_holder_id = current_user.id

    deleted_student = student_service.delete_student_by_id(
        license_holder_id,
        student_id,
    )

    return DeletedStudentResponse(
        id=deleted_student.id,
        username=deleted_student.username,
        message=f"Student with id {deleted_student.id} deleted successfully"
    )

@router.patch("/{student_id}")
def update_student(
    student_id: UUID,
    body: UpdateStudentRequest,
    student_service: StudentServiceDEP,
    current_user: AuthenticatedUserDEP,
):
    license_holder_id = current_user.id

    updated_student = student_service.update_student_by_id(
        license_holder_id,
        student_id,
        body.username,
    )

    return PatchedStudentResponse(
        id=updated_student.id,
        username=updated_student.username,
        message=f"Student with id {updated_student.id} updated successfully"
        )