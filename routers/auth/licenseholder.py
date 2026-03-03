# routers/users.py
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends, HTTPException, HTTPException

from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.licenseholders.LicenseHolderSessionReponse import LicenseHolderSessionResponse
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.licenseholders.LicenseHolderResponse import LicenseHolderResponse
from dependencies import get_license_holder_auth_service
from models.requests import LicenseHolderSignupRequest, LicenseHolderSigninRequest
from services import LicenseHolderAuthService
LicenseHolderAuthServiceDEP = Annotated[LicenseHolderAuthService, Depends(get_license_holder_auth_service)]

router = APIRouter(prefix="/auth/licenseholder", tags=["auth-licenseholder"])

@router.post("/signup", response_model=LicenseHolderSessionResponse ,status_code=201)
def signup_licenseholder(body: LicenseHolderSignupRequest, licenseholder_service: LicenseHolderAuthServiceDEP):
    session_response= licenseholder_service.signup_license_holder(body)
    return LicenseHolderSessionResponse(licenseholder=LicenseHolderResponse(id=session_response.licenseholder.id,email=session_response.licenseholder.email,username=session_response.licenseholder.user_metadata.get("username")),session=session_response.session) 

@router.post("/signin", response_model=LicenseHolderSessionResponse ,status_code=201)
def signin_licenseholder(body: LicenseHolderSigninRequest, licenseholder_service: LicenseHolderAuthServiceDEP):
    session_response= licenseholder_service.signin_license_holder(body)
    return LicenseHolderSessionResponse(licenseholder=LicenseHolderResponse(id=session_response.licenseholder.id,email=session_response.licenseholder.email,username=session_response.licenseholder.user_metadata.get("username")),session=session_response.session) 

