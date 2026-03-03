from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.models.auth.AuthenticatedLicenseHolder import AuthenticatedLicenseHolder
from blustorymicroservices.BluStoryLicenseHolders.models.auth.AuthenticatedStudent import AuthenticatedStudent
from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.base import AppException
from fastapi import APIRouter, Depends

from dependencies import get_student_service, get_current_license_holder,get_current_student
from models.requests import CreateUserRequest, UpdateStudentRequest
from models.responses import CreatedStudentResponse, StudentResponse,DeletedStudentResponse, PatchedStudentResponse
from services import StudentService
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.students.StudentSessionResponse import StudentSessionResponse
from fastapi import HTTPException

StudentServiceDEP = Annotated[StudentService, Depends(get_student_service)]
AuthLicenseHolderDEP = Annotated[AuthenticatedLicenseHolder, Depends(get_current_license_holder)]

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=CreatedStudentResponse, status_code=201)
def create_student(
    body: CreateUserRequest,
    student_service: StudentServiceDEP,
    current_license_holder: AuthLicenseHolderDEP,
):
    license_holder_id = str(current_license_holder.id)

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
    current_license_holder: AuthLicenseHolderDEP,
):
    license_holder_id = current_license_holder.id

    students = student_service.get_students_by_license_holder(license_holder_id)

    return [
        StudentResponse(id=s.id, username=s.username)
        for s in students
    ]


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: UUID,
    student_service: StudentServiceDEP,
    current_license_holder: AuthLicenseHolderDEP,
):
    license_holder_id = current_license_holder.id

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
    current_license_holder: AuthLicenseHolderDEP,
):
    license_holder_id = current_license_holder.id

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
    current_license_holder: AuthLicenseHolderDEP,
):
    license_holder_id = current_license_holder.id

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
@router.post("/{student_id}/impersonate", response_model=StudentSessionResponse)
def impersonate_as_student(
    student_id: UUID,
    current_lh: AuthLicenseHolderDEP,
    service: StudentServiceDEP ,
):
    # Security check: does this student belong to the current license holder?
    student = service.get_student_by_id(current_lh.id, student_id)
    if not student:
        raise HTTPException(403, "You do not have permission to access this student")

    # Generate a valid session / tokens for the student
    session_data = service.generate_impersonated_session(student_id)

    return StudentSessionResponse(
        student=StudentResponse(id=student.id, username=student.username),
        session=session_data.session   # or access_token + refresh_token
    )