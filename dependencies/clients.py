
from blustorymicroservices.BluStoryLicenseHolders.settings import Settings
from blustorymicroservices.BluStoryLicenseHolders.settings.config import \
    get_settings
from fastapi import Depends
from supabase import Client, create_client


def get_supabase_client(settings: Settings = Depends(get_settings)) -> Client:
    return create_client(settings.supabase.url, settings.supabase.service_role_key)
