from blustorymicroservices.BluStoryOperators.dependencies import \
    get_supabase_client
from blustorymicroservices.BluStoryOperators.repository import \
    OrganisationsRepository, MembersRepository,OperatorsRepository

from fastapi import Depends
from supabase import Client


def get_member_repository(client: Client = Depends(get_supabase_client)) -> MembersRepository:
    return MembersRepository(client)

def get_operator_repository(client: Client = Depends(get_supabase_client)) -> OperatorsRepository:
    return OperatorsRepository(client)

def get_organisation_admin_repository(client: Client = Depends(get_supabase_client)) -> OrganisationsRepository:
    return OrganisationsRepository(client)