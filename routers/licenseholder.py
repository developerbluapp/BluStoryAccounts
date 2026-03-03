# routers/users.py
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.dependencies.auth import get_current_license_holder
from blustorymicroservices.BluStoryLicenseHolders.models.auth import AuthenticatedLicenseHolder
from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends

from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.licenseholders.LicenseHolderResponse import LicenseHolderResponse
from blustorymicroservices.BluStoryLicenseHolders.services import LicenseHolderService
from dependencies import get_license_holder_service
from services import LicenseHolderService

LicenseHolderDEP = Annotated[LicenseHolderService, Depends(get_license_holder_service)]
AuthenticatedUserDEP = Annotated[AuthenticatedLicenseHolder, Depends(get_current_license_holder)]
    
router = APIRouter(prefix="/licenseholder", tags=["licenseholder"])

@router.get("/me")                                   # ← protected route
async def get_my_profile(current_user: AuthenticatedUserDEP, license_holder_service: LicenseHolderDEP):         # ← protected route
    license_holder = license_holder_service.get_license_holder_by_id(current_user.id) # ← ensure license holder exists, otherwise raise 404
    return LicenseHolderResponse(
        id=license_holder.id,
        email=license_holder.email,
        username=license_holder.user_metadata.get("username"))