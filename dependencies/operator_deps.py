from fastapi import Depends, HTTPException, status
from uuid import UUID
from typing import Annotated

from blustorymicroservices.blustory_accounts_auth.dependencies.auth import get_current_organisation_admin

from blustorymicroservices.blustory_accounts_auth.dependencies.services import get_operator_service
from blustorymicroservices.blustory_accounts_auth.models.auth.AuthenticatedOrganisationAdmin import AuthenticatedOrganisationAdmin
from blustorymicroservices.blustory_accounts_auth.models.dtos.Operator import Operator
from blustorymicroservices.blustory_accounts_auth.models.exceptions.base import AppException
from blustorymicroservices.blustory_accounts_auth.services.OperatorService import OperatorService

OperatorServiceDEP = Annotated[OperatorService, Depends(get_operator_service)]

def get_operator_in_organisation(
    operator_id: UUID,
    current_org: Annotated[AuthenticatedOrganisationAdmin, Depends(get_current_organisation_admin)],
    operator_service: OperatorServiceDEP,
) -> Operator:
    """
    Dependency that:
    1. Loads the operator by ID
    2. Verifies it belongs to the current organisation
    3. Returns the operator object (or raises 404/403)
    """
    operator = operator_service.get_operator_by_id(operator_id)

    if operator is None:
        raise AppException(
            code="operator_not_found",
            message="Operator not found",
            status=status.HTTP_404_NOT_FOUND,
        )
    #print(operator.app_metadata.get("organisation_id"),current_org.organisation_id)

    if str(operator.app_metadata.get("organisation_id")) != str(current_org.organisation_id):
        raise AppException(
            code="forbidden_operator_access",
            message="This operator does not belong to your organisation",
            status=status.HTTP_403_FORBIDDEN,
        )

    return operator