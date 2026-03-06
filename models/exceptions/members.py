
from blustorymicroservices.BluStoryOperators.models.exceptions.base import AppException

class UserAlreadyExistsException(AppException):
    def __init__(self, username: str):
        super().__init__(
            code="USER_ALREADY_EXISTS",
            message=f"Username/email '{username}' is already registered",
            status=409  # or 400 — 409 is more semantically correct for conflicts
        )
class MemberNotFoundException(AppException):
    def __init__(self, member_id: str):
        super().__init__(
            code="STUDENT_NOT_FOUND",
            message=f"Member with ID '{member_id}' not found",
            status=404
        )