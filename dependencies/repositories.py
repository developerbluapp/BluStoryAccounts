from blustorymicroservices.BluStoryAccounts.dependencies import \
    get_supabase_client
from blustorymicroservices.BluStoryAccounts.repository import \
    OrganisationRepository, OrganisationAdminRepository, MembersRepository, OperatorsRepository, RoleRepository, UserRoleRepository

from fastapi import Depends
from supabase import Client


def get_member_repository(client: Client = Depends(get_supabase_client)) -> MembersRepository:
    return MembersRepository(client)

def get_operator_repository(client: Client = Depends(get_supabase_client)) -> OperatorsRepository:
    return OperatorsRepository(client)

def get_organisation_repository(client: Client = Depends(get_supabase_client)) -> OrganisationRepository:
    return OrganisationRepository(client)

def get_organisation_admin_repository(client: Client = Depends(get_supabase_client)) -> OrganisationAdminRepository:
    return OrganisationAdminRepository(client)

def get_role_repository(client: Client = Depends(get_supabase_client)) -> RoleRepository:
    return RoleRepository(client)

def get_user_role_repository(client: Client = Depends(get_supabase_client)) -> UserRoleRepository:
    return UserRoleRepository(client)