import os

from blustorymicroservices.BluStoryAccounts.clients.api.OrganisationClient import OrganisationClient
from blustorymicroservices.BluStoryAccounts.dependencies.clients import get_organisation_client
from blustorymicroservices.BluStoryAccounts.dependencies.repositories import \
    get_member_repository,get_operator_repository, get_organisation_admin_repository
from blustorymicroservices.BluStoryAccounts.repository import \
    OperatorsRepository, MembersRepository, OrganisationsRepository
from blustorymicroservices.BluStoryAccounts.services import OperatorService, MemberService, OperatorAuthService,MemberAuthService, OrganisationService

from blustorymicroservices.BluStoryAccounts.services.auth.OrganisationAuthService import OrganisationAuthService
from blustorymicroservices.BluStoryAccounts.settings import (
    EmailSettings, RoleSettings, Settings, SupabaseSettings)
from fastapi import Depends
from supabase import Client


def get_member_service(member_repo: MembersRepository = Depends(get_member_repository ), operator_repo: OperatorsRepository = Depends(get_operator_repository)) -> MemberService:
    return MemberService(member_repo, operator_repo)

def get_operator_service(operator_repo: OperatorsRepository = Depends(get_operator_repository),member_repo: MembersRepository = Depends(get_member_repository),organisation_client: OrganisationClient = Depends(get_organisation_client)) -> OperatorService:
    return OperatorService(operator_repo, member_repo, organisation_client)

def get_organisation_service(organisation_repo: OrganisationsRepository = Depends(get_organisation_admin_repository)) -> OrganisationService:
    return OrganisationService(organisation_repo)

def get_operator_auth_service(
    operator_repo: OperatorsRepository = Depends(get_operator_repository),
    member_repo: MembersRepository = Depends(get_member_repository),
) -> OperatorAuthService:
    return OperatorAuthService(operator_repo, member_repo)


def get_member_auth_service(member_repo: MembersRepository = Depends(get_member_repository)) -> MemberAuthService:
    return MemberAuthService(member_repo)

def get_organisation_auth_service(
    organisation_repo: OrganisationsRepository = Depends(get_organisation_admin_repository)
) -> OrganisationAuthService:
    return OrganisationAuthService(organisation_repo)