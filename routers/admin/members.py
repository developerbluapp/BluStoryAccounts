
from typing import Annotated, Any
from uuid import UUID

from fastapi import Query, Request

from blustorymicroservices.BluStoryAccounts.dependencies.services import get_member_service
from blustorymicroservices.BluStoryAccounts.models.auth.AuthenticatedOperator import AuthenticatedOperator
from blustorymicroservices.BluStoryAccounts.models.auth.AuthenticatedMember import AuthenticatedMember
from blustorymicroservices.BluStoryAccounts.models.dtos import AuthMember
from blustorymicroservices.BluStoryAccounts.models.dtos.UpdateMember import UpdateMember
from blustorymicroservices.BluStoryAccounts.models.exceptions.base import AppException
from fastapi import APIRouter, Depends

from blustorymicroservices.BluStoryAccounts.models.requests.CreateUserRequest import CreateUserRequest
from blustorymicroservices.BluStoryAccounts.models.requests.GenerateDeepLinkRequest import GenerateDeepLinkRequest
from blustorymicroservices.BluStoryAccounts.models.requests.ResetPinRequest import ResetPinRequest
from blustorymicroservices.BluStoryAccounts.models.requests.UpdateMemberRequest import UpdateMemberRequest
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.CreatedMemberResponse import CreatedMemberResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.DeletedMemberResponse import DeletedMemberResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.MemberResponse import MemberResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.PatchedMemberResponse import PatchedMemberResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.ResetPinResponse import ResetPinResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.MemberGenerateDeepLinkResponse import MemberGenerateDeepLinkResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.MemberSessionResponse import MemberSessionResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.MemberCountResponse import MemberCountResponse
from blustorymicroservices.BluStoryAccounts.models.auth.AuthenticatedOrganisationAdmin import AuthenticatedOrganisationAdmin
from blustorymicroservices.BluStoryAccounts.dependencies.auth import get_current_member, get_current_operator, get_current_organisation_admin
from fastapi import HTTPException
import bcrypt

from blustorymicroservices.BluStoryAccounts.services.MemberService import MemberService

MemberServiceDEP = Annotated[MemberService, Depends(get_member_service)]
AuthOperatorDEP = Annotated[AuthenticatedOperator, Depends(get_current_operator)]
AuthMemberDEP = Annotated[AuthenticatedMember, Depends(get_current_member)]
AuthAdminDEP = Annotated[AuthenticatedOrganisationAdmin, Depends(get_current_organisation_admin)]   
router = APIRouter(prefix="/admin/members", tags=["admin/members"])
    
@router.get("", response_model=list[MemberResponse])
def get_members(
    member_service: MemberServiceDEP,
    current_admin: AuthAdminDEP,
):
    members = member_service.get_members_by_organisation(current_admin.organisation_id)    
    return [
        MemberResponse(id=s.id, username=s.username, first_name=s.first_name)
        for s in members
    ]

@router.get("/count", response_model=MemberCountResponse)
def get_member_count(
    member_service: MemberServiceDEP,
    current_admin: AuthAdminDEP,
):
    organisation_id = current_admin.organisation_id
    count = member_service.get_member_count(organisation_id)
    return MemberCountResponse(count=count)

@router.get("/members", response_model=list[MemberResponse])
def get_members(
    member_service: MemberServiceDEP,
    current_admin: AuthAdminDEP,
):
    members = member_service.get_members_by_organisation(current_admin.organisation_id)
    
    return [
        MemberResponse(id=s.id, username=s.username, first_name=s.first_name)
        for s in members
    ]

@router.post("/generate-deep-link", response_model=MemberGenerateDeepLinkResponse)
async def generate_deep_link(body: GenerateDeepLinkRequest, member_service: MemberServiceDEP, current_admin: AuthAdminDEP):
    organisation_id = current_admin.organisation_id
    return member_service.generate_member_deep_link_as_admin(organisation_id,body.member_id)
