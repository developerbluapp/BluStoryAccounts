from blustorymicroservices.BluStoryAccounts.dependencies import \
    get_db_provider
from blustorymicroservices.BluStoryAccounts.dependencies.externalclients import get_db_provider, get_auth_provider
from blustorymicroservices.BluStoryAccounts.repository import \
    OrganisationsRepository, MembersRepository,OperatorsRepository

from fastapi import Depends
from supabase import Client


def get_member_repository(auth_client: Client = Depends(get_auth_provider),db_client: Client = Depends(get_db_provider)) -> MembersRepository:
    
    return MembersRepository(auth_client,db_client)

def get_operator_repository(auth_client: Client = Depends(get_auth_provider),db_client: Client = Depends(get_db_provider)) -> OperatorsRepository:
    return OperatorsRepository(auth_client,db_client)

def get_organisation_admin_repository(auth_client: Client = Depends(get_auth_provider),db_client: Client = Depends(get_db_provider)) -> OrganisationsRepository:
    return OrganisationsRepository(auth_client,db_client)