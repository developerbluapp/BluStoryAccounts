from blustorymicroservices.BluStoryLicenseHolders.dependencies import \
    get_supabase_client
from blustorymicroservices.BluStoryLicenseHolders.repository import \
    LicenseHoldersRepository, StudentsRepository

from fastapi import Depends
from supabase import Client


def get_student_repository(client: Client = Depends(get_supabase_client)) -> StudentsRepository:
    return StudentsRepository(client)

def get_license_holder_repository(client: Client = Depends(get_supabase_client)) -> LicenseHoldersRepository:
    return LicenseHoldersRepository(client)