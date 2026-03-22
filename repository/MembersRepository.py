import hashlib
import hmac
from http.client import HTTPException
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException

from blustorymicroservices.BluStoryAccounts.helpers.AuthHelper import AuthHelper
from blustorymicroservices.BluStoryAccounts.helpers.OrganisationHelper import OrganisationHelper
from blustorymicroservices.BluStoryAccounts.models.auth import UserRoles
from blustorymicroservices.BluStoryAccounts.models.dtos import \
    AuthOperator, AuthMember, Operator, OperatorSession,Member, MemberSession, Roles, Roles
from blustorymicroservices.BluStoryAccounts.models.dtos.MemberDeepLink import MemberDeepLink
from blustorymicroservices.BluStoryAccounts.models.dtos.UpdateMember import UpdateMember
from blustorymicroservices.BluStoryAccounts.models.exceptions.operators import UserSignupAlreadyExistsException
from blustorymicroservices.BluStoryAccounts.models.responses.api.members import ResetPinResponse
from blustorymicroservices.BluStoryAccounts.providers.interfaces.AuthProvider import AuthProvider
from blustorymicroservices.BluStoryAccounts.providers.interfaces.DatabaseProvider import DatabaseProvider
from blustorymicroservices.BluStoryAccounts.settings.config import \
    get_settings
from blustorymicroservices.BluStoryAccounts.settings.Settings import \
    Settings
from blustorymicroservices.BluStoryAccounts.models.responses import SupabaseUserResponse

from blustorymicroservices.BluStoryAccounts.models.exceptions.members import UserAlreadyExistsException
from gotrue.errors import AuthApiError
import secrets
import uuid
import bcrypt
class MembersRepository:
    def __init__(self, auth_client : AuthProvider,db_client :DatabaseProvider):
        self._db_client = db_client
        self._auth_client = auth_client
        self.settings = get_settings()
     

    def _build_member_email(self, username: str, operator_id: UUID, organisation_id: UUID) -> str:
            op = self._db_client.select_one("operators", {"id": str(operator_id)}, ["username"])
            if not op:
                raise ValueError("Operator does not exist.")

            org = self._db_client.select_one("organisations", {"id": str(organisation_id)}, ["name"])
            if not org:
                raise ValueError("Organisation does not exist.")

            org_name = OrganisationHelper.clean_organisation_name(org["name"])
            return f"{username}.{op['username']}.{org_name}{self.settings.email.suffix}"

    def _generate_pin(self, length: int = 4) -> str:
        return "".join(str(secrets.randbelow(10)) for _ in range(length))

    def generate_setup_link(self, username: str, operator_id: UUID, organisation_id: UUID) -> str:
        email = self._build_member_email(username, operator_id, organisation_id)
        return self._auth_client.generate_magic_link(email, redirect_to=self.settings.deeplink.url)

    def create_member(self, username: str, first_name: str, operator_id: UUID, organisation_id: UUID) -> Member:


        email = self._build_member_email(username, operator_id, organisation_id)
        password = AuthHelper.create_random_password()
        

        role_response = self._db_client.select_one("roles", {"name": UserRoles.STUDENT}, "*")
        if not role_response:
            raise ValueError("Student role not found")
        roles = Roles(roles=[role_response["name"]])

        try:
            user_data = self._auth_client.create_user(
                email=email,
                password=password,
                email_confirm=True,
                user_metadata={"avatar_url": "https://picsum.photos/id/237/200/300"},
                app_metadata={
                    "roles": [roles.model_dump()["roles"]],
                    "operator_id": str(operator_id),
                    "organisation_id": str(organisation_id),
                }
            )
            user_id = user_data.user.id

            self._db_client.insert("members", {
                "id": user_id,
                "username": username,
                "first_name": first_name,
                "operator_id": str(operator_id),
                "organisation_id": str(organisation_id),
            })

            self._db_client.insert("user_roles", {
                "user_id": user_id,
                "role_id": role_response["id"],
                "organisation_id": str(organisation_id),
            })

            return Member(id=user_id, username=username, first_name=first_name)

        except UserAlreadyExistsException:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to create member: {e}")

    def get_members_by_operator(self, operator_id: UUID) -> List[Member]:
        rows = self._db_client.select_many("members", {"operator_id": str(operator_id)})
        return [Member(**r) for r in rows]

    def get_member_by_id(self, operator_id: UUID, member_id: UUID) -> Optional[Member]:
        row = self._db_client.select_one("members", {
            "operator_id": str(operator_id),
            "id": str(member_id)
        })
        return Member(**row) if row else None

    def delete_member_by_id(self, operator_id: UUID, member_id: UUID) -> Optional[Member]:
        member = self.get_member_by_id(operator_id, member_id)
        if not member:
            return None
        self._auth_client.delete_user(member.id)
        self._db_client.delete("members", {"id": str(member.id)})
        return member

    def update_member_by_id(self, operator_id: UUID, member_id: UUID, update_data: UpdateMember) -> Optional[Member]:
        member = self.get_member_by_id(operator_id, member_id)
        if not member:
            return None
        changes = update_data.model_dump(exclude_none=True)
        self._db_client.update("members", {"id": str(member_id), "operator_id": str(operator_id)}, changes)
        return self.get_member_by_id(operator_id, member_id)

    def reset_member_pin(self, member_id: UUID) -> ResetPinResponse:
        pin = self._generate_pin(4)
        pin_hash = bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
        updated = self._db_client.update("members", {"id": str(member_id)}, {"pin_hash": pin_hash})
        if not updated:
            raise ValueError("Member not found")
        return ResetPinResponse(member_id=member_id, pin=pin)