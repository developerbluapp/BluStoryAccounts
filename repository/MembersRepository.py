import hashlib
import hmac
from http.client import HTTPException
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
from blustorymicroservices.BluStoryAccounts.settings.config import \
    get_settings
from blustorymicroservices.BluStoryAccounts.settings.Settings import \
    Settings
from blustorymicroservices.BluStoryAccounts.models.responses import SupabaseUserResponse
from supabase import Client, create_client
from blustorymicroservices.BluStoryAccounts.models.exceptions.members import UserAlreadyExistsException
from gotrue.errors import AuthApiError
import secrets
import uuid
import bcrypt
class MembersRepository:
    def __init__(self, client: Client):
        self._client = client
     

    def _build_member_email(self, username: str,operator_id:str,organisation_id:str) -> str:
        # TODO You would want a request from the routes and get the data but couldn't be bothered.
        operator_response = self._client.table("operators").select("username").eq("id", str(operator_id)).maybe_single().execute()
        if not operator_response:
            raise HTTPException(status_code=404, detail="Operator does not exist.")
        organisation_response = self._client.table("organisations").select("name").eq("id", str(organisation_id)).maybe_single().execute()
        if not organisation_response:
            raise HTTPException(status_code=404, detail="Organisation does not exist.")
        operator_username = operator_response.data["username"]
        organisation_name = organisation_response.data["name"]
        organisation_name = OrganisationHelper.clean_organisation_name(organisation_name)
        return f"{username}.{operator_username}.{organisation_name}{get_settings().email.suffix}"
    

    def _generate_pin(self,length=4) -> str:
        # Generates a random numeric PIN e.g. "7392"
        return "".join([str(secrets.randbelow(10)) for _ in range(length)])
    def generate_setup_link(self, username: str,operator_id:UUID,organisation_id: UUID) -> str:
        settings = get_settings()
        fake_email = self._build_member_email(username,operator_id,organisation_id)
        link_response = self._client.auth.admin.generate_link({
            "type": "magiclink",
            "email": fake_email,
            "options": {
                "redirect_to": settings.deeplink.url
            }
        })

        return link_response.properties.action_link

    def create_member(self,username: str,first_name:str,operator_id: UUID,organisation_id :UUID) -> Member:
        
        try:


            role_response = self._client.table("roles").select("*").eq("name", UserRoles.STUDENT).maybe_single().execute()
            if not role_response:
                raise HTTPException(status_code=404, detail="Role does not exist.")


            fake_email = self._build_member_email(username,operator_id,organisation_id)
            print(f"Creating member with email: {fake_email}")  # Debug log
            password = AuthHelper.create_random_password()
            roles = Roles(roles=[role_response.data["name"]])
            response = self._client.auth.admin.create_user({
                "email": fake_email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"avatar_url": "https://picsum.photos/id/237/200/300"},
                "app_metadata": {"roles": roles.model_dump()["roles"],
                                "operator_id": operator_id,
                                "organisation_id":str(organisation_id) } 
            })
            self._client.table("members").insert({
            "id": str(response.user.id),
            "username": username,
            "first_name":first_name,
            "operator_id": str(operator_id),
            "organisation_id":str(organisation_id)
            }).execute()
            self._client.table("user_roles").insert({
                "user_id": response.user.id,
                "role_id": role_response.data["id"],
                "organisation_id":str(organisation_id)
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
        if not response:
            raise HTTPException(status_code=404,detail="No Members exist.")

        return [Member(**s) for s in response.data]

    def get_members_by_organisation(self, organisation_id: UUID) -> list[Member]:
        response = self._client.table("members")\
            .select("*")\
            .eq("organisation_id", str(organisation_id))\
            .execute()
        return [Member(**s) for s in response.data]

    def count_members_by_organisation(self, organisation_id: UUID) -> int:
        response = self._client.table("members")\
            .select("id")\
            .eq("organisation_id", str(organisation_id))\
            .execute()
        return len(response.data)

    def get_member_by_id(self, operator_id: UUID, member_id: UUID) -> Member | None:
        response = self._client.table("members")\
            .select("*")\
            .eq("operator_id", str(operator_id))\
            .eq("id", str(member_id))\
            .maybe_single()\
            .execute()
        if not response:
             raise HTTPException(status_code=404,detail="Member does not exist.")
        return Member(id=response.data["id"], username=response.data["username"], first_name=response.data["first_name"]) if response else None


    def delete_member_by_id(self, operator_id: UUID, member_id: UUID) -> Member | None:
        member = self.get_member_by_id(operator_id,member_id)
        if not member:
            return None
        self._client.auth.admin.delete_user(member.id)
        self._client.table("members").delete().eq("id", str(member.id)).execute()
        return member  # return what was deleted so caller can confirm
    def update_member_by_id(self, operator_id: UUID, member_id: UUID,update_data:UpdateMember) -> Member | None:
        member = self.get_member_by_id(operator_id, member_id)
        if not member:
            return None
        update_dict = update_data.model_dump(exclude_none=True)
       
        self._client.table("members") \
            .update(update_dict) \
            .eq("operator_id", str(operator_id)) \
            .eq("id", str(member.id)) \
            .execute()

        # optionally re-fetch updated member
        return self.get_member_by_id(operator_id, member_id)

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
        email = self._build_member_email(member["username"])
        link_response = self._client.auth.admin.generate_link({
            "type": "magiclink",
            "email": email
        })
        return MemberDeepLink(member_id=member_id, deep_link=link_response.properties.action_link)