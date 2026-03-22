from blustorymicroservices.BluStoryAccounts.dependencies import \
    get_auth_client
from blustorymicroservices.BluStoryAccounts.dependencies.externalclients import get_auth_client, get_db_client
from blustorymicroservices.BluStoryAccounts.repository import \
    OrganisationsRepository, MembersRepository,OperatorsRepository

from fastapi import Depends
from supabase import Client


def get_member_repository(auth_client: Client = Depends(get_auth_client),db_client: Client = Depends(get_db_client)) -> MembersRepository:
    return MembersRepository(auth_client,db_client)

def get_operator_repository(auth_client: Client = Depends(get_auth_client),db_client: Client = Depends(get_db_client)) -> OperatorsRepository:
    return OperatorsRepository(auth_client,db_client)

def get_organisation_admin_repository(auth_client: Client = Depends(get_auth_client),db_client: Client = Depends(get_db_client)) -> OrganisationsRepository:
    return OrganisationsRepository(auth_client,db_client)