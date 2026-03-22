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

@router.post("/signin", response_model=MemberSessionResponse ,status_code=201)
def signin_member(body: MemberSigninRequest, member_service: MemberAuthServiceDEP):
    session_response= member_service.signin_member(body)
    return MemberSessionResponse(member=MemberResponse(id=session_response.member.id,username=session_response.member.username),session=session_response.session) 


# ── PIN login (called from member tablet) ────────────────────────
@router.post("/pin-login/{member_id}", response_model=MemberDeepLinkResponse)
async def pin_login(member_id: UUID, body: PinLoginRequest, member_service: MemberAuthServiceDEP):
    member = member_service.pin_signin_member(member_id, body.pin)
    return MemberDeepLinkResponse(member_id=member.member_id, deep_link=member.deep_link)

@router.get("/callback")
async def callback(request: Request):
    params = dict(request.query_params)  # {"key": "value", ...}
    print("Received query parameters:", params)

    # Process the parameters as needed
    # For example, you could return them in the response
    return {"received_params": params}