# routers/users.py
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends, HTTPException, HTTPException

from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.LicenseHolderSessionReponse import LicenseHolderSessionResponse
from dependencies import get_auth_service
from models.requests import SignupRequest
from models.responses import CreatedStudentResponse
from services import AuthService
from models.responses import SignedupResponse
AuthServiceDEP = Annotated[AuthService, Depends(get_auth_service)]

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=LicenseHolderSessionResponse ,status_code=201)
def signup_licenseholder(body: SignupRequest, service: AuthServiceDEP):
    session_response= service.signup_license_holder(body)
    return LicenseHolderSessionResponse(**session_response.model_dump()) 

