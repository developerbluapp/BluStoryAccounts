from fastapi import Depends
from supabase import Client
from blustorymicroservices.BluStoryLicenseHolders.repository import SupabaseUserRepository
from blustorymicroservices.BluStoryLicenseHolders.dependencies import get_supabase_client

def get_user_repository(client: Client = Depends(get_supabase_client)) -> SupabaseUserRepository:
    return SupabaseUserRepository(client)

