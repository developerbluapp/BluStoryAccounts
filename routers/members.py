from typing import Annotated, Any
from uuid import UUID

from fastapi import Query, Request

from blustorymicroservices.BluStoryOperators.models.auth.AuthenticatedOperator import AuthenticatedOperator
from blustorymicroservices.BluStoryOperators.models.auth.AuthenticatedMember import AuthenticatedMember
from blustorymicroservices.BluStoryOperators.models.dtos import AuthMember
from blustorymicroservices.BluStoryOperators.models.exceptions.base import AppException
from fastapi import APIRouter, Depends

from blustorymicroservices.BluStoryOperators.models.requests.GenerateDeepLinkRequest import GenerateDeepLinkRequest
from blustorymicroservices.BluStoryOperators.models.requests.ResetPinRequest import ResetPinRequest
from blustorymicroservices.BluStoryOperators.models.responses.api.members.ResetPinResponse import ResetPinResponse
from blustorymicroservices.BluStoryOperators.models.responses.api.members.MemberGenerateDeepLinkResponse import MemberGenerateDeepLinkResponse
from dependencies import get_member_service, get_current_operator,get_current_member
from models.requests import CreateUserRequest, UpdateMemberRequest
from models.responses import CreatedMemberResponse, MemberResponse,DeletedMemberResponse, PatchedMemberResponse
from services import MemberService
from blustorymicroservices.BluStoryOperators.models.responses.api.members.MemberSessionResponse import MemberSessionResponse
from fastapi import HTTPException
import bcrypt
MemberServiceDEP = Annotated[MemberService, Depends(get_member_service)]
AuthOperatorDEP = Annotated[AuthenticatedOperator, Depends(get_current_operator)]
AuthMemberDEP = Annotated[AuthenticatedMember, Depends(get_current_member)]
router = APIRouter(prefix="/members", tags=["members"])

@router.post("/reset-pin", response_model=ResetPinResponse)
async def reset_pin(body: ResetPinRequest, member_service: MemberServiceDEP):
    return member_service.reset_member_pin(body.member_id)

@router.post("/generate-deep-link", response_model=MemberGenerateDeepLinkResponse)
async def generate_deep_link(body: GenerateDeepLinkRequest, member_service: MemberServiceDEP, current_operator: AuthOperatorDEP):
    operator_id = current_operator.id
    return member_service.generate_member_deep_link(operator_id, body.member_id)

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
    operator_id = str(current_operator.id)
    return member_service.register_member(
        body.username,
        body.first_name,
        operator_id=operator_id,
    )


@router.get("", response_model=list[MemberResponse])
def get_members(
    member_service: MemberServiceDEP,
    current_operator: AuthOperatorDEP,
):
    operator_id = current_operator.id

    members = member_service.get_members_by_operator(operator_id)

    return [
        MemberResponse(id=s.id, username=s.username,first_name=s.first_name)
        for s in members
    ]


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
def update_member(
    member_id: UUID,
    body: UpdateMemberRequest,
    member_service: MemberServiceDEP,
    current_operator: AuthOperatorDEP,
):
    operator_id = current_operator.id

    updated_member = member_service.update_member_by_id(
        operator_id,
        member_id,
        body.username,
    )

    return PatchedMemberResponse(
        id=updated_member.id,
        username=updated_member.username,
        message=f"Member with id {updated_member.id} updated successfully"
        )

