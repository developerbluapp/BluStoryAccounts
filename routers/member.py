# routers/users.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, HTTPException,Request



from blustorymicroservices.blustory_accounts_auth.models.dtos.MemberDeepLink import MemberDeepLink
from blustorymicroservices.blustory_accounts_auth.models.requests import PinLoginRequest
from blustorymicroservices.blustory_accounts_auth.models.responses.api.members.MemberDeepLinkResponse import MemberDeepLinkResponse
from blustorymicroservices.blustory_accounts_auth.models.requests import MemberSigninRequest
from blustorymicroservices.blustory_accounts_auth.models.responses import CreatedMemberResponse

from blustorymicroservices.blustory_accounts_auth.models.responses.api.members.MemberSessionResponse import MemberSessionResponse
from blustorymicroservices.blustory_accounts_auth.models.responses.api.members.MemberResponse import MemberResponse
from blustorymicroservices.blustory_accounts_auth.services.auth.MemberAuthService import MemberAuthService
from blustorymicroservices.extras.BluStoryAccountsOld.dependencies.services import get_member_auth_service

router = APIRouter(prefix="/auth/member", tags=["auth-member"])
MemberAuthServiceDEP = Annotated[MemberAuthService, Depends(get_member_auth_service)]

@router.post("/generate-setup-link", response_model=MemberSessionResponse ,status_code=201)
def generate_setup_link(email: str, member_service: MemberAuthServiceDEP):
    deep_link = member_service.generate_setup_link(email)
    return MemberDeepLinkResponse(deep_link=deep_link)
