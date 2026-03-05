import os

from blustorymicroservices.BluStoryLicenseHolders.dependencies.repositories import \
    get_member_repository,get_license_holder_repository
from blustorymicroservices.BluStoryLicenseHolders.repository import \
    LicenseHoldersRepository, MembersRepository
from blustorymicroservices.BluStoryLicenseHolders.services import LicenseHolderService, MemberService, LicenseHolderAuthService,MemberAuthService

from blustorymicroservices.BluStoryLicenseHolders.settings import (
    EmailSettings, RoleSettings, Settings, SupabaseSettings)
from fastapi import Depends
from supabase import Client


def get_member_service(member_repo: MembersRepository = Depends(get_member_repository ), license_holder_repo: LicenseHoldersRepository = Depends(get_license_holder_repository)) -> MemberService:
    return MemberService(member_repo, license_holder_repo)

def get_license_holder_service(license_holder_repo: LicenseHoldersRepository = Depends(get_license_holder_repository),member_repo: MembersRepository = Depends(get_member_repository)) -> LicenseHolderService:
    return LicenseHolderService(license_holder_repo, member_repo)

def get_license_holder_auth_service(
    license_holder_repo: LicenseHoldersRepository = Depends(get_license_holder_repository),
    member_repo: MembersRepository = Depends(get_member_repository),
) -> LicenseHolderAuthService:
    return LicenseHolderAuthService(license_holder_repo, member_repo)


def get_member_auth_service(member_repo: MembersRepository = Depends(get_member_repository)) -> MemberAuthService:
    return MemberAuthService(member_repo)