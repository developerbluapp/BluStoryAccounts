# routers/users.py
from ast import Or
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryAccounts.dependencies.auth import  get_current_organisation_admin
from blustorymicroservices.BluStoryAccounts.dependencies.services import get_operator_service, get_organisation_service
from blustorymicroservices.BluStoryAccounts.helpers.AuthHelper import AuthHelper
from blustorymicroservices.BluStoryAccounts.models.auth import AuthenticatedOperator,AuthenticatedOrganisationAdmin
from blustorymicroservices.BluStoryAccounts.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends

from blustorymicroservices.BluStoryAccounts.models.requests import CreateOperatorRequest
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.CreatedOperatorResponse import CreatedOperatorResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.CreateOrganisationAdminResponse import CreatedOrganisationAdminResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.OrganisationNameResponse import OrganisationNameResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.OrganisationAdminResponse import OrganisationAdminResponse
from blustorymicroservices.BluStoryAccounts.services import OperatorService, OrganisationService
from blustorymicroservices.BluStoryAccounts.dependencies import get_current_operator
from blustorymicroservices.BluStoryAccounts.services import OperatorService
from blustorymicroservices.BluStoryAccounts.models.requests.AddToOrganisationRequest import AddToOrganisationRequest
OperatorServiceDEP = Annotated[OperatorService, Depends(get_operator_service)]
AuthenticatedOrganisationAdminDEP = Annotated[AuthenticatedOrganisationAdmin, Depends(get_current_organisation_admin)]
AuthenticatedOperatorDEP = Annotated[AuthenticatedOperator, Depends(get_current_operator)]
OrganisationServiceDEP = Annotated[OrganisationService, Depends(get_organisation_service)]
router = APIRouter(prefix="/admin/organisation", tags=["organisation"])



@router.post("/assign", response_model=CreatedOrganisationAdminResponse)
def create_and_assign_organisation_admin(
    body: AddToOrganisationRequest,
    organisation_service: OrganisationServiceDEP,
    current_organisation_admin: AuthenticatedOrganisationAdminDEP,
):
    organisation_id = current_organisation_admin.organisation_id
    
    email = body.email
    return organisation_service.create_and_assign_organisation_admin(email,organisation_id)

