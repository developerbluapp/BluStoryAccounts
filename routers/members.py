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
router = APIRouter(prefix="/members", tags=["members"])

@router.post("/generate-deep-link", response_model=MemberGenerateDeepLinkResponse)
async def generate_deep_link(body: GenerateDeepLinkRequest, member_service: MemberServiceDEP, current_operator: AuthOperatorDEP):
    operator_id = current_operator.id
    organisation_id = current_operator.organisation_id
    return member_service.generate_member_deep_link(operator_id, body.member_id,organisation_id)

@router.get("/profile", response_model=MemberResponse)
def get_my_member(
    member_service: MemberServiceDEP,
    current_member: AuthMemberDEP,
):
    return member_service.get_member_by_id(
        current_member.operator_id,
        current_member.id)


@router.post("", response_model=CreatedMemberResponse, status_code=201)
def create_member(
    body: CreateUserRequest,
    member_service: MemberServiceDEP,
    current_operator: AuthOperatorDEP,
):  
    organisation_id = current_operator.organisation_id
    operator_id = str(current_operator.id)
    return member_service.register_member(
        body.username,
        body.first_name,
        operator_id=operator_id,
        organisation_id=organisation_id
    )


@router.get("", response_model=list[MemberResponse])
def get_members(
    member_service: MemberServiceDEP,
    current_operator: AuthOperatorDEP,
):
    members = member_service.get_members_by_operator(current_operator.id)
    
    return [
        MemberResponse(id=s.id, username=s.username, first_name=s.first_name)
        for s in members
    ]

@router.get("/count", response_model=MemberCountResponse)
def get_member_count(
    member_service: MemberServiceDEP,
    current_operator: AuthOperatorDEP
):
    organisation_id = current_operator.organisation_id
    count = member_service.get_member_count(organisation_id)
    return MemberCountResponse(count=count)


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
    member_id: UUID,
    member_service: MemberServiceDEP,
    current_operator: AuthOperatorDEP,
):
    operator_id = current_operator.id

    member = member_service.get_member_by_id(
        operator_id,
        member_id,
    )

    if not member:
        raise AppException(
            code="member_not_found",
            message="Member not found",
            status=404,
        )
    return MemberResponse(
        id=member.id,
        username=member.username,
        first_name=member.first_name
    )



@router.delete("/{member_id}")
def delete_member(
    member_id: UUID,
    member_service: MemberServiceDEP,
    current_operator: AuthOperatorDEP,
):
    operator_id = current_operator.id

    deleted_member = member_service.delete_member_by_id(
        operator_id,
        member_id,
    )
    if not deleted_member:
        raise AppException(
            code="member_not_found",
            message="Member not found",
            status=404,
        )

    return DeletedMemberResponse(
        id=deleted_member.id,
        username=deleted_member.username,
        message=f"Member with id {deleted_member.id} deleted successfully"
    )

@router.patch("/{member_id}")
def update_username(
    member_id: UUID,
    body: UpdateMemberRequest,
    member_service: MemberServiceDEP,
    current_operator: AuthOperatorDEP,
):
    operator_id = current_operator.id
    update_data = UpdateMember()

    if body.username is not None:
        update_data.username = body.username

    if body.first_name is not None:
        update_data.first_name = body.first_name


    if body.username is not None or body.first_name is not None:
        updated_member = member_service.update_member_by_id(
            operator_id,
            member_id,
            body
        )
    return PatchedMemberResponse(
        id=updated_member.id,
        username=updated_member.username,
        message=f"Member with id {updated_member.id} updated successfully"
        )

