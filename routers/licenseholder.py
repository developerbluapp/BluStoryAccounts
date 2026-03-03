# routers/users.py
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.dependencies.auth import get_current_user
from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends

from dependencies import get_user_service
from models.requests import CreateUserRequest,UpdateStudentRequest
from models.responses import CreatedStudentResponse
from services import StudentService
from models.responses import StudentResponse
StudentServiceDEP = Annotated[StudentService, Depends(get_user_service)]

router = APIRouter(prefix="/licenseholder", tags=["licenseholder"])


@router.get("/me")                                   # ← protected route
async def get_my_profile(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.user_metadata.get("username"),
        "role": current_user.app_metadata.get("role")
    }