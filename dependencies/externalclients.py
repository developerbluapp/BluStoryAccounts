
from blustorymicroservices.BluStoryAccounts.settings import Settings
from blustorymicroservices.BluStoryAccounts.settings.config import \
    get_settings
from fastapi import Depends
from supabase import Client, create_client
from blustorymicroservices.BluStoryAccounts.clients.api.OrganisationClient import OrganisationClient


def get_db_client(settings: Settings = Depends(get_settings)) -> Client:
    return create_client(settings.supabase.url, settings.supabase.service_role_key)

def get_auth_client(settings: Settings = Depends(get_settings)) -> Client:
    return create_client(settings.supabase.url, settings.supabase.service_role_key)


