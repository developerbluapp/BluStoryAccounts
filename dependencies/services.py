import os

from blustorymicroservices.BluStoryOperators.dependencies.repositories import \
    get_member_repository,get_license_holder_repository
from blustorymicroservices.BluStoryOperators.repository import \
    OperatorsRepository, MembersRepository
from blustorymicroservices.BluStoryOperators.services import OperatorService, MemberService, OperatorAuthService,MemberAuthService

from blustorymicroservices.BluStoryOperators.settings import (
    EmailSettings, RoleSettings, Settings, SupabaseSettings)
from fastapi import Depends
from supabase import Client


def get_member_service(member_repo: MembersRepository = Depends(get_member_repository ), license_holder_repo: OperatorsRepository = Depends(get_license_holder_repository)) -> MemberService:
    return MemberService(member_repo, license_holder_repo)

def get_license_holder_service(license_holder_repo: OperatorsRepository = Depends(get_license_holder_repository),member_repo: MembersRepository = Depends(get_member_repository)) -> OperatorService:
    return OperatorService(license_holder_repo, member_repo)

def get_license_holder_auth_service(
    license_holder_repo: OperatorsRepository = Depends(get_license_holder_repository),
    member_repo: MembersRepository = Depends(get_member_repository),
) -> OperatorAuthService:
    return OperatorAuthService(license_holder_repo, member_repo)


def get_member_auth_service(member_repo: MembersRepository = Depends(get_member_repository)) -> MemberAuthService:
    return MemberAuthService(member_repo)