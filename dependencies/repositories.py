from blustorymicroservices.BluStoryAccounts.dependencies import \
    get_supabase_client
from blustorymicroservices.BluStoryAccounts.repository import \
    OrganisationRepository, OrganisationAdminRepository, MembersRepository, OperatorsRepository, RoleRepository, UserRoleRepository

from fastapi import Depends
from supabase import Client


def get_member_repository(client: Client = Depends(get_supabase_client, use_cache=False)) -> MembersRepository:
    return MembersRepository(client)

def get_operator_repository(client: Client = Depends(get_supabase_client, use_cache=False)) -> OperatorsRepository:
    return OperatorsRepository(client)

def get_organisation_repository(client: Client = Depends(get_supabase_client, use_cache=False)) -> OrganisationRepository:
    return OrganisationRepository(client)

def get_organisation_admin_repository(client: Client = Depends(get_supabase_client, use_cache=False)) -> OrganisationAdminRepository:
    return OrganisationAdminRepository(client)

def get_role_repository(client: Client = Depends(get_supabase_client, use_cache=False)) -> RoleRepository:
    return RoleRepository(client)

def get_user_role_repository(client: Client = Depends(get_supabase_client, use_cache=False)) -> UserRoleRepository:
    return UserRoleRepository(client)