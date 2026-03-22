
from blustorymicroservices.BluStoryAccounts.providers.interfaces.AuthProvider import AuthProvider
from blustorymicroservices.BluStoryAccounts.providers.interfaces.DatabaseProvider import DatabaseProvider
from blustorymicroservices.BluStoryAccounts.providers.supabase.SupabaseAuthProvider import SupabaseAuthProvider
from blustorymicroservices.BluStoryAccounts.providers.supabase.SupabaseDatabaseProvider import SupabaseDatabaseProvider
from blustorymicroservices.BluStoryAccounts.repository.MembersRepository import MembersRepository
from blustorymicroservices.BluStoryAccounts.settings import Settings
from blustorymicroservices.BluStoryAccounts.settings.config import \
    get_settings
from fastapi import Depends
from supabase import Client, create_client
from blustorymicroservices.BluStoryAccounts.clients.api.OrganisationClient import OrganisationClient


def get_supabase_client(
    settings: Settings = Depends(get_settings)
) -> Client:
    """Single shared client — service role key = admin powers"""
    return create_client(
        supabase_url=settings.supabase.url,
        supabase_key=settings.supabase.service_role_key
    )


def get_auth_provider(
    client: Client = Depends(get_supabase_client)
) -> AuthProvider:
    return SupabaseAuthProvider(client)


def get_db_provider(
    client: Client = Depends(get_supabase_client)
) -> DatabaseProvider:
    return SupabaseDatabaseProvider(client)

