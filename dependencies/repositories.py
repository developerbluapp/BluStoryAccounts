from blustorymicroservices.BluStoryOperators.dependencies import \
    get_supabase_client
from blustorymicroservices.BluStoryOperators.repository import \
    OperatorsRepository, MembersRepository

from fastapi import Depends
from supabase import Client


def get_member_repository(client: Client = Depends(get_supabase_client)) -> MembersRepository:
    return MembersRepository(client)

def get_operator_repository(client: Client = Depends(get_supabase_client)) -> OperatorsRepository:
    return OperatorsRepository(client)