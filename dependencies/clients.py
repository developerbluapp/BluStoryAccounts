
from blustorymicroservices.blustory_accounts_auth.settings import Settings
from blustorymicroservices.blustory_accounts_auth.settings.config import \
    get_settings
from fastapi import Depends
from supabase import Client, create_client
from blustorymicroservices.blustory_accounts_auth.clients.api.OrganisationClient import OrganisationClient
from blustorymicroservices.blustory_accounts_auth.dependencies.auth import get_bearer_token


def get_organisation_client(settings: Settings = Depends(get_settings), access_token: str = Depends(get_bearer_token)) -> OrganisationClient:
    return OrganisationClient(settings.internal_clients.organisation_service_url, access_token)
