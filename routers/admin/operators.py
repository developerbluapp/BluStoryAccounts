# routers/users.py
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryOperators.dependencies.auth import get_current_operator, get_current_organisation_admin
from blustorymicroservices.BluStoryOperators.models.auth import AuthenticatedOperator,AuthenticatedOrganisationAdmin
from blustorymicroservices.BluStoryOperators.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends

from blustorymicroservices.BluStoryOperators.models.requests import CreateOperatorRequest
from blustorymicroservices.BluStoryOperators.models.responses.api.operators.CreatedOperatorResponse import CreatedOperatorResponse
from blustorymicroservices.BluStoryOperators.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.BluStoryOperators.services import OperatorService
from dependencies import get_operator_service
from services import OperatorService

OperatorServiceDEP = Annotated[OperatorService, Depends(get_operator_service)]
AuthenticatedOrganisationAdminDEP = Annotated[AuthenticatedOrganisationAdmin, Depends(get_current_organisation_admin)]
AuthenticatedOperatorDEP = Annotated[AuthenticatedOperator, Depends(get_current_operator)]
    
router = APIRouter(prefix="/admin/operator", tags=["admin_operator"])



@router.post("", response_model=CreatedOperatorResponse, status_code=201)
def create_operator(
    operator_service: OperatorServiceDEP,
    current_organisation: AuthenticatedOrganisationAdminDEP,
):
    organisation_id = current_organisation.organisation_id
    return operator_service.register_operator(organisation_id)


@router.get("", response_model=list[OperatorResponse])
def get_operators(
    operator_service: OperatorServiceDEP,
    current_organisation: AuthenticatedOrganisationAdminDEP,
):
    organisation_id = current_organisation.id

    operators = operator_service.get_operators_by_organisation(organisation_id)

    return [
        OperatorResponse(id=s.id, username=s.username, email=s.email)
        for s in operators
    ]
"""

@router.get("/{operator_id}", response_model=OperatorResponse)
def get_operator(
    operator_id: UUID,
    operator_service: OperatorServiceDEP,
    current_organisation: AuthenticatedOrganisationAdminDEP,
):
    organisation_id = current_organisation.id

    operator = operator_service.get_operator_by_id(
        operator_id,
        operator_id,
    )

    if not operator:
        raise AppException(
            code="operator_not_found",
            message="Operator not found",
            status=404,
        )
    return OperatorResponse(
        id=operator.id,
        username=operator.username,
        first_name=operator.first_name
    )



@router.delete("/{operator_id}")
def delete_operator(
    operator_id: UUID,
    operator_service: OperatorServiceDEP,
    current_organisation: AuthenticatedOrganisationAdminDEP,
):
    organisation_id = current_organisation.id

    deleted_operator = operator_service.delete_operator_by_id(
        operator_id,
        operator_id,
    )
    if not deleted_operator:
        raise AppException(
            code="operator_not_found",
            message="Operator not found",
            status=404,
        )

    return DeletedOperatorResponse(
        id=deleted_operator.id,
        username=deleted_operator.username,
        message=f"Operator with id {deleted_operator.id} deleted successfully"
    )

@router.patch("/{operator_id}")
def update_operator(
    operator_id: UUID,
    body: UpdateOperatorRequest,
    operator_service: OperatorServiceDEP,
    current_organisation: AuthenticatedOrganisationAdminDEP,
):
    organisation_id = current_organisation.id

    updated_operator = operator_service.update_operator_by_id(
        operator_id,
        operator_id,
        body.username,
    )

    return PatchedOperatorResponse(
        id=updated_operator.id,
        username=updated_operator.username,
        message=f"Operator with id {updated_operator.id} updated successfully"
        )

"""