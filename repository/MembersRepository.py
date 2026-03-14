import hashlib
import hmac
from http.client import HTTPException
from uuid import UUID

from fastapi import HTTPException

from blustorymicroservices.BluStoryOperators.models.auth import UserRoles
from blustorymicroservices.BluStoryOperators.models.dtos import \
    AuthOperator, AuthMember, Operator, OperatorSession,Member, MemberSession, Roles, Roles
from blustorymicroservices.BluStoryOperators.models.dtos.MemberDeepLink import MemberDeepLink
from blustorymicroservices.BluStoryOperators.models.exceptions.operators import UserSignupAlreadyExistsException
from blustorymicroservices.BluStoryOperators.models.responses.api.members import ResetPinResponse
from blustorymicroservices.BluStoryOperators.settings.config import \
    get_settings
from blustorymicroservices.BluStoryOperators.settings.Settings import \
    Settings
from blustorymicroservices.BluStoryOperators.models.responses import SupabaseUserResponse
from supabase import Client, create_client
from blustorymicroservices.BluStoryOperators.models.exceptions.members import UserAlreadyExistsException
from gotrue.errors import AuthApiError
import secrets
import uuid
import bcrypt
class MembersRepository:
    def __init__(self, client: Client):
        self._client = client
     
    def _build_email(self, username: str) -> str:
        return f"{username}{get_settings().email.suffix}"
    

    def _generate_pin(self,length=4) -> str:
        # Generates a random numeric PIN e.g. "7392"
        return "".join([str(secrets.randbelow(10)) for _ in range(length)])
    def generate_setup_link(self, username: str) -> str:
        settings = get_settings()
        fake_email = self._build_email(username)
        print(f"settings.deeplink.url: {settings.deeplink.url}")
        link_response = self._client.auth.admin.generate_link({
            "type": "magiclink",
            "email": fake_email,
            "options": {
                "redirect_to": settings.deeplink.url
            }
        })

        return link_response.properties.action_link
    def _derive_password(self, plain_pin: str) -> str:
        secret = get_settings().pin.secret
        return hmac.new(
            secret.encode(),
            plain_pin.encode(),
            hashlib.sha256
        ).hexdigest()
    def create_member(self,username: str,first_name:str,operator_id: UUID) -> Member:
        
        try:
            # Auto-generate PIN instead of accepting one from request
            plain_pin = self._generate_pin(4)
            role_response = self._client.table("roles").select("*").eq("name", UserRoles.STUDENT).maybe_single().execute()
            fake_email = self._build_email(username)
            password = self._derive_password(plain_pin)
            roles = Roles(roles=[role_response.data["name"]])
            response = self._client.auth.admin.create_user({
                "email": fake_email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"avatar_url": "https://picsum.photos/id/237/200/300"},
                "app_metadata": {"roles": roles.model_dump()["roles"],
                                "operator_id": operator_id } 
            })
            self._client.table("members").insert({
            "id": str(response.user.id),
            "username": username,
            "first_name":first_name,
            "operator_id": str(operator_id)
            }).execute()
            self._client.table("user_roles").insert({
                "user_id": response.user.id,
                "role_id": role_response.data["id"]
            }).execute()
            
            if not response:
                raise HTTPException(status_code=500, detail="Failed to insert member record")

            return Member(
                id=response.user.id,
                username=username,
                first_name=first_name
            )
        except AuthApiError as e:
            if "already been registered" in str(e):
                raise UserAlreadyExistsException(username=username)
            else:
                raise
    def get_members_by_operator(self, operator_id: UUID) -> list[Member]:
        response = self._client.table("members")\
            .select("*")\
            .eq("operator_id", str(operator_id))\
            .execute()
        return [Member(**s) for s in response.data]

    def get_member_by_id(self, operator_id: UUID, member_id: UUID) -> Member | None:
        response = self._client.table("members")\
            .select("*")\
            .eq("operator_id", str(operator_id))\
            .eq("id", str(member_id))\
            .maybe_single()\
            .execute()
        return Member(id=response.data["id"], username=response.data["username"], first_name=response.data["first_name"]) if response else None


    def delete_member_by_id(self, operator_id: UUID, member_id: UUID) -> Member | None:
        member = self.get_member_by_id(operator_id,member_id)
        if not member:
            return None
        self._client.auth.admin.delete_user(member.id)
        self._client.table("members").delete().eq("id", str(member.id)).execute()
        return member  # return what was deleted so caller can confirm
    def update_member_by_id(self, operator_id: UUID, member_id: UUID, new_username: str) -> Member | None:
        member = self.get_member_by_id(operator_id, member_id)
        if not member:
            return None
        self._client.table("members").update({"username": new_username}).eq("operator_id", str(operator_id)).eq("id", str(member.id)).execute()
        return Member(id=member.id, username=new_username, first_name=member.first_name)  # return updated member
    def signin_member(self, auth_member_dto: AuthMember) -> MemberSession:
        try:
            session_response = self._client.auth.sign_in_with_password({
                "email": f"{auth_member_dto.username}{get_settings().email.suffix}",
                "password": auth_member_dto.password
            })
            if "error" in session_response and session_response["error"]:
                raise HTTPException(status_code=400, detail=session_response["error"]["message"])
            user_response = self._client.auth.get_user(session_response.session.access_token)
            #member = self._map_supabase_auth_user_to_member(SupabaseUserResponse(**user_response.user.model_dump()))
            #return MemberSession(member=member, session=session_response.session)
        except AuthApiError as e:
            raise HTTPException(status_code=400, detail=str(e))
    def reset_member_pin(self, member_id: UUID) -> ResetPinResponse:
        new_pin = self._generate_pin(4)
        pin_hash = bcrypt.hashpw(new_pin.encode(), bcrypt.gensalt()).decode()
        result = self._client.table("members").update({
            "pin_hash": pin_hash
        }).eq("id", str(member_id)).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Member not found")

        return ResetPinResponse(member_id=member_id, pin=new_pin)
    def pin_signin_member(self, member_id: UUID, pin: str) -> MemberDeepLink:
                # 1. Find member by tablet ID
        result = self._client.table("members").select(
            "id, username, pin_hash"
        ).eq("member_id", member_id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Tablet not registered")

        member = result.data

        # 2. Verify PIN
        is_valid = bcrypt.checkpw(
            pin.encode(),
            member["pin_hash"].encode()
        )
        if not is_valid:
            raise HTTPException(status_code=401, detail="Incorrect PIN")

        # 3. Generate a magic link session for the member
        email = self._build_email(member["username"])
        link_response = self._client.auth.admin.generate_link({
            "type": "magiclink",
            "email": email
        })
        return MemberDeepLink(member_id=member_id, deep_link=link_response.properties.action_link)