import os
from fastapi import Depends
from supabase import Client
from blustorymicroservices.BluStoryLicenseHolders.dependencies.repositories import get_user_repository
from blustorymicroservices.BluStoryLicenseHolders.settings import Settings, SupabaseSettings, EmailSettings, RoleSettings
from blustorymicroservices.BluStoryLicenseHolders.repository import SupabaseUserRepository
from blustorymicroservices.BluStoryLicenseHolders.services import UserService
    
def get_user_service(repo: SupabaseUserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)

