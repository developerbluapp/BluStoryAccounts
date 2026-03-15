
from blustorymicroservices.BluStoryOperators.settings import Settings
from blustorymicroservices.BluStoryOperators.settings.config import \
    get_settings
from fastapi import Depends
from supabase import Client, create_client
from blustorymicroservices.BluStoryOperators.clients.api.OrganisationClient import OrganisationClient


def get_supabase_client(settings: Settings = Depends(get_settings)) -> Client:
    return create_client(settings.supabase.url, settings.supabase.service_role_key)


