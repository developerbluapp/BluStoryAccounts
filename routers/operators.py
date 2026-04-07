from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryAccounts.dependencies.auth import get_current_operator, get_current_organisation_admin
from blustorymicroservices.BluStoryAccounts.models.auth import AuthenticatedOperator,AuthenticatedOrganisationAdmin
from blustorymicroservices.BluStoryAccounts.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends

from blustorymicroservices.BluStoryAccounts.models.requests import CreateOperatorRequest
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.CreatedOperatorResponse import CreatedOperatorResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.ResetOperatorPasswordResponse import ResetOperatorPasswordResponse
from blustorymicroservices.BluStoryAccounts.services import OperatorService
from blustorymicroservices.BluStoryAccounts.dependencies import get_operator_service
from blustorymicroservices.BluStoryAccounts.services import OperatorService

OperatorServiceDEP = Annotated[OperatorService, Depends(get_operator_service)]
AuthenticatedOrganisationAdminDEP = Annotated[AuthenticatedOrganisationAdmin, Depends(get_current_organisation_admin)]
AuthenticatedOperatorDEP = Annotated[AuthenticatedOperator, Depends(get_current_operator)]
    
router = APIRouter(prefix="/operator", tags=["admin_operator"])

@router.get("/me")                                   # ← protected route
async def get_my_profile(current_user: AuthenticatedOperatorDEP, operator_service: OperatorServiceDEP):         # ← protected route
    operator = operator_service.get_operator_by_id(current_user.id) # ← ensure license holder exists, otherwise raise 404
    return OperatorResponse(
        id=operator.id,
        email=operator.email)
@router.post("/reset-password/{operator_id}", response_model=ResetOperatorPasswordResponse, status_code=201)
def reset_password(
    operator_id: UUID,
    operator_service: OperatorServiceDEP,
    current_organisation: AuthenticatedOperatorDEP,
):
    organisation_id = current_organisation.organisation_id

    return operator_service.reset_password(organisation_id, operator_id)
