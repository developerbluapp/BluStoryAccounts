
from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.base import AppException

class UserSignupAlreadyExistsException(AppException):
    def __init__(self, email: str):
        super().__init__(
            code="USER_SIGNUP_ALREADY_EXISTS",
            message=f"Email '{email}' is already registered",
            status=409  # or 400 — 409 is more semantically correct for conflicts
        )