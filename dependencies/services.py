import os

from blustorymicroservices.BluStoryOperators.dependencies.repositories import \
    get_member_repository,get_operator_repository
from blustorymicroservices.BluStoryOperators.repository import \
    OperatorsRepository, MembersRepository
from blustorymicroservices.BluStoryOperators.services import OperatorService, MemberService, OperatorAuthService,MemberAuthService

from blustorymicroservices.BluStoryOperators.settings import (
    EmailSettings, RoleSettings, Settings, SupabaseSettings)
from fastapi import Depends
from supabase import Client


def get_member_service(member_repo: MembersRepository = Depends(get_member_repository ), operator_repo: OperatorsRepository = Depends(get_operator_repository)) -> MemberService:
    return MemberService(member_repo, operator_repo)

def get_operator_service(operator_repo: OperatorsRepository = Depends(get_operator_repository),member_repo: MembersRepository = Depends(get_member_repository)) -> OperatorService:
    return OperatorService(operator_repo, member_repo)

def get_operator_auth_service(
    operator_repo: OperatorsRepository = Depends(get_operator_repository),
    member_repo: MembersRepository = Depends(get_member_repository),
) -> OperatorAuthService:
    return OperatorAuthService(operator_repo, member_repo)


def get_member_auth_service(member_repo: MembersRepository = Depends(get_member_repository)) -> MemberAuthService:
    return MemberAuthService(member_repo)