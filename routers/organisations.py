# routers/users.py
from ast import Or
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryAccounts.dependencies.auth import  get_current_organisation_admin
from blustorymicroservices.BluStoryAccounts.dependencies.services import get_operator_service, get_organisation_service
from blustorymicroservices.BluStoryAccounts.models.auth import AuthenticatedOperator,AuthenticatedOrganisationAdmin
from blustorymicroservices.BluStoryAccounts.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends

from blustorymicroservices.BluStoryAccounts.models.requests import CreateOperatorRequest
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.CreatedOperatorResponse import CreatedOperatorResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.OrganisationNameResponse import OrganisationNameResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.OrganisationResponse import OrganisationResponse
from blustorymicroservices.BluStoryAccounts.services import OperatorService, OrganisationService
from dependencies import get_current_operator
from services import OperatorService

OperatorServiceDEP = Annotated[OperatorService, Depends(get_operator_service)]
AuthenticatedOrganisationAdminDEP = Annotated[AuthenticatedOrganisationAdmin, Depends(get_current_organisation_admin)]
AuthenticatedOperatorDEP = Annotated[AuthenticatedOperator, Depends(get_current_operator)]
OrganisationServiceDEP = Annotated[OrganisationService, Depends(get_organisation_service)]
router = APIRouter(prefix="/organisations", tags=["organisations"])




@router.get("/{organisation_id}", response_model=OrganisationNameResponse)
def get_organisation_name(
    organisation_id: UUID,
    organisation_service: OrganisationServiceDEP,
    current_organisation_admin: AuthenticatedOrganisationAdminDEP,
):
    current_organisation_id = current_organisation_admin.organisation_id
    print(current_organisation_id,"current organisation id in router",organisation_id)
    if current_organisation_id != organisation_id:
        raise AppException(
            code="forbidden",
            message="You do not have access to this resource",
            status=403,
        )


    organisation_name = organisation_service.get_organisation_name_by_id(organisation_id)
    print(organisation_name,"organisation name in router")

    if not organisation_name:
        raise AppException(
            code="organisation_name_not_found",
            message="Operator not found",
            status=404,
        )
    return OrganisationNameResponse(id=organisation_id, organisation_name=organisation_name)

