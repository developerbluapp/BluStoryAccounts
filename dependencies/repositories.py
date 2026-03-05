from blustorymicroservices.BluStoryLicenseHolders.dependencies import \
    get_supabase_client
from blustorymicroservices.BluStoryLicenseHolders.repository import \
    LicenseHoldersRepository, MembersRepository

from fastapi import Depends
from supabase import Client


def get_member_repository(client: Client = Depends(get_supabase_client)) -> MembersRepository:
    return MembersRepository(client)

def get_license_holder_repository(client: Client = Depends(get_supabase_client)) -> LicenseHoldersRepository:
    return LicenseHoldersRepository(client)