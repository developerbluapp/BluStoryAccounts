import os
from fastapi import Depends
from supabase import create_client, Client
from blustorymicroservices.BluStoryLicenseHolders.settings import Settings, SupabaseSettings, EmailSettings, RoleSettings
from blustorymicroservices.BluStoryLicenseHolders.repository import SupabaseUserRepository
from blustorymicroservices.BluStoryLicenseHolders.services import UserService

from functools import lru_cache
from blustorymicroservices.BluStoryLicenseHolders.settings.config import get_settings

def get_supabase_client(settings: Settings = Depends(get_settings)) -> Client:
    return create_client(settings.supabase.url, settings.supabase.service_role_key)


def get_user_repository(client: Client = Depends(get_supabase_client)) -> SupabaseUserRepository:
    return SupabaseUserRepository(client)



def get_user_service(repo: SupabaseUserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)




