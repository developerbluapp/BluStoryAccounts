# routers/users.py
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryOperators.dependencies.auth import get_current_license_holder
from blustorymicroservices.BluStoryOperators.models.auth import AuthenticatedOperator
from blustorymicroservices.BluStoryOperators.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends

from blustorymicroservices.BluStoryOperators.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.BluStoryOperators.services import OperatorService
from dependencies import get_license_holder_service
from services import OperatorService

OperatorDEP = Annotated[OperatorService, Depends(get_license_holder_service)]
AuthenticatedUserDEP = Annotated[AuthenticatedOperator, Depends(get_current_license_holder)]
    
router = APIRouter(prefix="/operator", tags=["operator"])

@router.get("/me")                                   # ← protected route
async def get_my_profile(current_user: AuthenticatedUserDEP, license_holder_service: OperatorDEP):         # ← protected route
    license_holder = license_holder_service.get_license_holder_by_id(current_user.id) # ← ensure license holder exists, otherwise raise 404
    return OperatorResponse(
        id=license_holder.id,
        email=license_holder.email)