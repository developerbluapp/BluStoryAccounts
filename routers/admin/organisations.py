# routers/users.py
from ast import Or
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryOperators.dependencies.auth import  get_current_organisation_admin
from blustorymicroservices.BluStoryOperators.dependencies.services import get_operator_service, get_organisation_service
from blustorymicroservices.BluStoryOperators.helpers.AuthHelper import AuthHelper
from blustorymicroservices.BluStoryOperators.models.auth import AuthenticatedOperator,AuthenticatedOrganisationAdmin
from blustorymicroservices.BluStoryOperators.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends

from blustorymicroservices.BluStoryOperators.models.requests import CreateOperatorRequest
from blustorymicroservices.BluStoryOperators.models.responses.api.operators.CreatedOperatorResponse import CreatedOperatorResponse
from blustorymicroservices.BluStoryOperators.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.BluStoryOperators.models.responses.api.organisations.CreateOrganisationAdminResponse import CreatedOrganisationAdminResponse
from blustorymicroservices.BluStoryOperators.models.responses.api.organisations.OrganisationNameResponse import OrganisationNameResponse
from blustorymicroservices.BluStoryOperators.models.responses.api.organisations.OrganisationResponse import OrganisationResponse
from blustorymicroservices.BluStoryOperators.services import OperatorService, OrganisationService
from dependencies import get_current_operator
from services import OperatorService
from blustorymicroservices.BluStoryOperators.models.requests.AddToOrganisationRequest import AddToOrganisationRequest
OperatorServiceDEP = Annotated[OperatorService, Depends(get_operator_service)]
AuthenticatedOrganisationAdminDEP = Annotated[AuthenticatedOrganisationAdmin, Depends(get_current_organisation_admin)]
AuthenticatedOperatorDEP = Annotated[AuthenticatedOperator, Depends(get_current_operator)]
OrganisationServiceDEP = Annotated[OrganisationService, Depends(get_organisation_service)]
router = APIRouter(prefix="/admin/organisation", tags=["organisation"])



@router.post("/{organisation_id}/admins", response_model=CreatedOrganisationAdminResponse)
def create_and_assign_organisation_admin(
    organisation_id: UUID,
    body: AddToOrganisationRequest,
    organisation_service: OrganisationServiceDEP,
    current_organisation_admin: AuthenticatedOrganisationAdminDEP,
):
    current_organisation_id = current_organisation_admin.organisation_id
    if current_organisation_id != organisation_id:
        raise AppException(
            code="forbidden",
            message="You do not have access to this resource",
            status=403,
        )
    
    email = body.email
    return organisation_service.create_and_assign_organisation_admin(email,organisation_id)

