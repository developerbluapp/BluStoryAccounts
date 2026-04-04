from fastapi import Depends
from blustorymicroservices.blustory_accounts_auth.interfaces.AuthProvider import AuthProvider
from blustorymicroservices.blustory_accounts_auth.dependencies.externalclients import get_auth_provider
from blustorymicroservices.blustory_accounts_auth.services.auth.OperatorAuthService import OperatorAuthService
from blustorymicroservices.blustory_accounts_auth.services.auth.OrganisationAuthService import OrganisationAuthService

def get_operator_auth_service(
    auth_provider: AuthProvider = Depends(get_auth_provider)
) -> OperatorAuthService:
    return OperatorAuthService(auth_provider)

def get_organisation_auth_service(
    auth_provider: AuthProvider = Depends(get_auth_provider)
) -> OrganisationAuthService:
    return OrganisationAuthService(auth_provider)