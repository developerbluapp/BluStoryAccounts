
from blustorymicroservices.blustory_accounts_auth.providers.interfaces.AuthProvider import AuthProvider
from blustorymicroservices.blustory_accounts_auth.providers.supabase.SupabaseAuthProvider import SupabaseAuthProvider
from blustorymicroservices.blustory_accounts_auth.settings import Settings
from blustorymicroservices.blustory_accounts_auth.settings.config import get_settings
from fastapi import Depends
from supabase import Client, create_client

def get_supabase_client(
    settings: Settings = Depends(get_settings)
) -> Client:
    """Single shared client — service role key = admin powers"""
    print("Seititit",settings)
    return create_client(
        supabase_url=settings.supabase.url,
        supabase_key=settings.supabase.service_role_key
    )

def get_auth_provider(
    client: Client = Depends(get_supabase_client)
) -> AuthProvider:
    return SupabaseAuthProvider(client)