# routers/users.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, HTTPException,Request

from blustorymicroservices.BluStoryAccounts.dependencies.services import get_member_auth_service
from blustorymicroservices.BluStoryAccounts.models.dtos.MemberDeepLink import MemberDeepLink
from blustorymicroservices.BluStoryAccounts.models.requests import PinLoginRequest
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.MemberDeepLinkResponse import MemberDeepLinkResponse
from blustorymicroservices.BluStoryAccounts.models.requests import MemberSigninRequest
from blustorymicroservices.BluStoryAccounts.models.responses import CreatedMemberResponse
from blustorymicroservices.BluStoryAccounts.services import MemberAuthService
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.MemberSessionResponse import MemberSessionResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.MemberResponse import MemberResponse
MemberAuthServiceDEP = Annotated[MemberAuthService, Depends(get_member_auth_service)]

router = APIRouter(prefix="/auth/member", tags=["auth-member"])


# Member Signin is via deep_link no auth needed.