
from supabase import create_client, Client
from fastapi import Depends
from blustorymicroservices.BluStoryLicenseHolders.settings import Settings
from blustorymicroservices.BluStoryLicenseHolders.settings import Settings
from blustorymicroservices.BluStoryLicenseHolders.settings.config import get_settings

    
def get_supabase_client(settings: Settings = Depends(get_settings)) -> Client:
    return create_client(settings.supabase.url, settings.supabase.service_role_key)

