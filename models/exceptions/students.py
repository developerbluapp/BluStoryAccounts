
from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.base import AppException

class UserAlreadyExistsException(AppException):
    def __init__(self, username: str):
        super().__init__(
            code="USER_ALREADY_EXISTS",
            message=f"Username/email '{username}' is already registered",
            status=409  # or 400 — 409 is more semantically correct for conflicts
        )
class StudentNotFoundException(AppException):
    def __init__(self, student_id: str):
        super().__init__(
            code="STUDENT_NOT_FOUND",
            message=f"Student with ID '{student_id}' not found",
            status=404
        )