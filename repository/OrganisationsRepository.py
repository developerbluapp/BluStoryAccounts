from http.client import HTTPException
from urllib import response
from uuid import UUID,uuid4

from fastapi import HTTPException

from blustorymicroservices.BluStoryAccounts.models.auth import UserRoles
from blustorymicroservices.BluStoryAccounts.models.dtos import \
    AuthOrganisation, OrganisationAdmin, OrganisationSession,Member, Roles
from blustorymicroservices.BluStoryAccounts.models.dtos.Organisation import Organisation
from blustorymicroservices.BluStoryAccounts.models.exceptions.organisations import UserSignupAlreadyExistsException
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.CreateOrganisationAdminResponse import CreatedOrganisationAdminResponse
from blustorymicroservices.BluStoryAccounts.settings.config import \
    get_settings
from blustorymicroservices.BluStoryAccounts.settings.Settings import \
    Settings
from blustorymicroservices.BluStoryAccounts.models.responses import SupabaseUserResponse
from supabase import Client, create_client
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.OrganisationAdminResponse import OrganisationAdminResponse
from blustorymicroservices.BluStoryAccounts.models.exceptions.members import UserAlreadyExistsException
from gotrue.errors import AuthApiError

class OrganisationsRepository:
    def __init__(self, client: Client):
        self._client = client

    def _map_supabase_auth_user_to_organisation(self, user: SupabaseUserResponse, organisation_id:UUID,organisation_name: str) -> OrganisationAdmin:
        return OrganisationAdmin(
            id=user.id,
            organisation_id=organisation_id,
            organisation_name=organisation_name,
            email=user.email,
            phone=user.phone,
            email_confirmed_at=user.email_confirmed_at,
            phone_confirmed_at=user.phone_confirmed_at,
            confirmed_at=user.confirmed_at,
            last_sign_in_at=user.last_sign_in_at,
            app_metadata=user.app_metadata,
            user_metadata=user.user_metadata,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_anonymous=user.is_anonymous
        )
    def _get_role_id(self, role_name: str) -> str:
        role_response = self._client.table("roles").select("id").eq("name", role_name).maybe_single().execute()
        if not role_response:
            raise HTTPException(status_code=500, detail=f"Role '{role_name}' not found in database")
        else:
            return role_response.data["id"]
    def get_organisation_by_name(self, organisation_name: str) -> Organisation:
        org_record = self._client.table("organisations").select("*").eq("name", organisation_name).maybe_single().execute()
        if not org_record:
            raise HTTPException(status_code=404, detail="Organisation not found")
        data = org_record.data
        return Organisation(id=data["id"], name=data["name"], created_at=data["created_at"])
    def get_organisation_by_id(self, organisation_id: UUID) -> Organisation:
        org_record = self._client.table("organisations").select("*").eq("id", str(organisation_id)).maybe_single().execute()
        if not org_record:
            raise HTTPException(status_code=404, detail="Organisation not found")
        data = org_record.data
        return Organisation(id=data["id"], name=data["name"], created_at=data["created_at"])
    def get_organisation_name_by_id(self, organisation_id: UUID) -> str | None:
        org_record = self._client.table("organisations").select("name").eq("id", str(organisation_id)).maybe_single().execute()
        if not org_record:
            return HTTPException(status_code=404, detail="OrganisationAdmin not found")
        return org_record.data["name"]
    def signup_organisation(self, auth_organisation_dto: AuthOrganisation) -> OrganisationSession:
        try:

            org_check = self._client.table("organisations") \
                .select("*") \
                .eq("name", auth_organisation_dto.organisation_name) \
                .maybe_single() \
                .execute()
            if org_check is not None:
                raise HTTPException(
                    status_code=400,
                    detail=f"OrganisationAdmin '{auth_organisation_dto.organisation_name}' already exists"
                )

            # 1️⃣ Get organisation admin role
            role_response = self._client.table("roles") \
                .select("*") \
                .eq("name", UserRoles.ORGANISATION_ADMIN) \
                .maybe_single() \
                .execute()

            roles = Roles(roles=[role_response.data["name"]])
            organisation_id = str(uuid4())

            # 2️⃣ Create the user (organisation admin)
            response = self._client.auth.admin.create_user({
                "email": auth_organisation_dto.email,
                "password": auth_organisation_dto.password,
                "email_confirm": True,
                "user_metadata": {"avatar_url": "https://picsum.photos/id/237/200/300"},
                "app_metadata": {"organisation_id": organisation_id, "roles": roles.model_dump()["roles"]}
            })

            

            self._client.table("organisations").insert({
                "id": organisation_id,
                "name": auth_organisation_dto.organisation_name
            }).execute()

            # 4️⃣ Assign user role scoped to organisation
            self._client.table("user_roles").insert({
                "user_id": response.user.id,
                "role_id": role_response.data["id"],
                "organisation_id": organisation_id
            }).execute()

            # 5️⃣ Sign in user to get session
            session_response = self._client.auth.sign_in_with_password({
                "email": auth_organisation_dto.email,
                "password": auth_organisation_dto.password
            })

            if "error" in session_response and session_response["error"]:
                raise HTTPException(status_code=400, detail=session_response["error"]["message"])

            organisation = self._map_supabase_auth_user_to_organisation(
                SupabaseUserResponse(**response.user.model_dump())
                ,organisation_id=organisation_id
                ,organisation_name=auth_organisation_dto.organisation_name
            )

            return OrganisationSession(
                organisation=organisation,
                session=session_response.session
            )

        except AuthApiError as e:
            if "already been registered" in str(e):
                raise UserSignupAlreadyExistsException(email=auth_organisation_dto.email, organisation=auth_organisation_dto.organisation_name)
            else:
                raise
    def signin_organisation(self, auth_organisation_dto: AuthOrganisation) -> OrganisationSession:
        try:
            role_id =  self._get_role_id(UserRoles.ORGANISATION_ADMIN)
            # 1️⃣ Sign in user
            session_response = self._client.auth.sign_in_with_password({
                "email": auth_organisation_dto.email,
                "password": auth_organisation_dto.password
            })

            if "error" in session_response and session_response["error"]:
                raise HTTPException(
                    status_code=400,
                    detail=session_response["error"]["message"]
                )
            
            # 2️⃣ Fetch user info
            user_response = self._client.auth.get_user(session_response.session.access_token)
            # 3️⃣ Get the user's organisation(s) from user_roles
            user_roles_resp = self._client.table("user_roles") \
                .select("organisation_id") \
                .eq("user_id", str(user_response.user.id)) \
                .eq("role_id",str(role_id)) \
                .maybe_single() \
                .execute()


            if not user_roles_resp:
                raise HTTPException(
                    status_code=400,
                    detail="OrganisationAdmin admin role not assigned"
                )
            
            organisation_id = user_roles_resp.data["organisation_id"]

            org_record = self._client.table("organisations") \
                .select("name") \
                .eq("id", organisation_id) \
                .maybe_single() \
                .execute()
            if not org_record:
                raise HTTPException(
                    status_code=400,
                    detail="OrganisationAdmin not found for user"
                )
            

            organisation_name = org_record.data["name"]
        

            # 5️⃣ Map user to OrganisationAdmin DTO including organisation name
            organisation = self._map_supabase_auth_user_to_organisation(
                SupabaseUserResponse(**user_response.user.model_dump()),
                organisation_id=organisation_id,
                organisation_name=organisation_name
            )

            # 6️⃣ Return session
            return OrganisationSession(
                organisation=organisation,
                session=session_response.session
            )

        except AuthApiError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    def create_and_assign_organisation_admin(self, email:str,password:str, organisation_name: str) -> CreatedOrganisationAdminResponse:
        try:
            # 0️⃣ Find the existing organisation
            org = self._client.table("organisations") \
                .select("*") \
                .eq("name", organisation_name) \
                .maybe_single() \
                .execute()

            if not org:
                raise HTTPException(
                    status_code=404,
                    detail=f"OrganisationAdmin '{organisation_name}' not found"
                )

            organisation_id = org.data["id"]
            
            # 1️⃣ Get organisation admin role
            role_response = self._client.table("roles") \
                .select("*") \
                .eq("name", UserRoles.ORGANISATION_ADMIN) \
                .maybe_single() \
                .execute()

            roles = Roles(roles=[role_response.data["name"]])

            # 2️⃣ Create new admin user
            response = self._client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"avatar_url": "https://picsum.photos/id/237/200/300"},
                "app_metadata": {"organisation_id": organisation_id,"roles": roles.model_dump()["roles"]}
            })

            # 3️⃣ Assign organisation_admin role to this user
            self._client.table("user_roles").insert({
                "user_id": response.user.id,
                "role_id": role_response.data["id"],
                "organisation_id": str(organisation_id)
            }).execute()
            

            return CreatedOrganisationAdminResponse(id=response.user.id,email=email,password=password,organisation_id=organisation_id)
        except AuthApiError as e:
            if "already been registered" in str(e):
                raise UserSignupAlreadyExistsException(email=email, organisation=organisation_name)
            else:
                raise