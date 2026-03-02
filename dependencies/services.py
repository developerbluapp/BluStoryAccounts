import os

from blustorymicroservices.BluStoryLicenseHolders.dependencies.repositories import \
    get_user_repository
from blustorymicroservices.BluStoryLicenseHolders.repository import \
    SupabaseUserRepository
from blustorymicroservices.BluStoryLicenseHolders.services import UserService
from blustorymicroservices.BluStoryLicenseHolders.settings import (
    EmailSettings, RoleSettings, Settings, SupabaseSettings)
from fastapi import Depends
from supabase import Client


def get_user_service(repo: SupabaseUserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)

