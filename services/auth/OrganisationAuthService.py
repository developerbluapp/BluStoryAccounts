from uuid import UUID, uuid4
from fastapi import HTTPException
from blustorymicroservices.BluStoryAccounts.models.dtos import \
    AuthOrganisation, AuthOrganisation, OrganisationSession, Roles
from blustorymicroservices.BluStoryAccounts.models.auth import UserRoles
from blustorymicroservices.BluStoryAccounts.repository.OrganisationRepository import OrganisationRepository
from blustorymicroservices.BluStoryAccounts.repository.OrganisationAdminRepository import OrganisationAdminRepository
from blustorymicroservices.BluStoryAccounts.models.responses import SupabaseUserResponse
from supabase import Client
from gotrue.errors import AuthApiError
from blustorymicroservices.BluStoryAccounts.models.exceptions.organisations import UserSignupAlreadyExistsException

class OrganisationAuthService:
    def __init__(self, organisation_repo: OrganisationRepository, admin_repo: OrganisationAdminRepository, supabase_client: Client):
        self._organisation_repo = organisation_repo
        self._admin_repo = admin_repo
        self._supabase_client = supabase_client

    def signup_organisation(self, auth_organisation_dto: AuthOrganisation) -> OrganisationSession:
        try:
            # 1. Check if organisation already exists
            try:
                self._organisation_repo.get_organisation_by_name(auth_organisation_dto.organisation_name)
                raise HTTPException(status_code=400, detail=f"Organisation '{auth_organisation_dto.organisation_name}' already exists")
            except HTTPException as e:
                if e.status_code != 404:
                    raise

            # 2. Get role
            role_id = self._admin_repo.get_role_id(UserRoles.ORGANISATION_ADMIN)
            organisation_id = str(uuid4())
            roles_dto = Roles(roles=[UserRoles.ORGANISATION_ADMIN])

            # 3. Create user (Auth)
            response = self._supabase_client.auth.admin.create_user({
                "email": auth_organisation_dto.email,
                "password": auth_organisation_dto.password,
                "email_confirm": True,
                "user_metadata": {"avatar_url": "https://picsum.photos/id/237/200/300"},
                "app_metadata": {"organisation_id": organisation_id, "roles": roles_dto.model_dump()["roles"]}
            })

            # 4. Create organisation (DB)
            self._organisation_repo.create_organisation(organisation_id, auth_organisation_dto.organisation_name)

            # 5. Assign role and link to org (DB)
            self._admin_repo.assign_role(response.user.id, role_id, organisation_id)
            self._admin_repo.link_to_org(response.user.id, organisation_id)

            # 6. Sign in to get session
            session_response = self._supabase_client.auth.sign_in_with_password({
                "email": auth_organisation_dto.email,
                "password": auth_organisation_dto.password
            })

            if "error" in session_response and session_response["error"]:
                raise HTTPException(status_code=400, detail=session_response["error"]["message"])

            admin_dto = self._admin_repo.map_user_to_admin(
                SupabaseUserResponse(**response.user.model_dump()),
                organisation_id=UUID(organisation_id),
                organisation_name=auth_organisation_dto.organisation_name
            )

            return OrganisationSession(
                organisation=admin_dto,
                session=session_response.session
            )

        except AuthApiError as e:
            if "already been registered" in str(e):
                raise UserSignupAlreadyExistsException(email=auth_organisation_dto.email, organisation=auth_organisation_dto.organisation_name)
            raise

    def signin_organisation(self, auth_organisation_dto: AuthOrganisation) -> OrganisationSession:
        try:
            # 1. Sign in
            session_response = self._supabase_client.auth.sign_in_with_password({
                "email": auth_organisation_dto.email,
                "password": auth_organisation_dto.password
            })

            if "error" in session_response and session_response["error"]:
                raise HTTPException(status_code=400, detail=session_response["error"]["message"])
            
            # 2. Fetch user info
            user_response = self._supabase_client.auth.get_user(session_response.session.access_token)
            
            # 3. Get organisation linked to this admin
            organisation_id_str = self._admin_repo.get_admin_organisation_id(user_response.user.id)
            organisation_id = UUID(organisation_id_str)
            organisation_name = self._organisation_repo.get_organisation_name_by_id(organisation_id)

            # 4. Map and return
            admin_dto = self._admin_repo.map_user_to_admin(
                SupabaseUserResponse(**user_response.user.model_dump()),
                organisation_id=organisation_id,
                organisation_name=organisation_name
            )

            return OrganisationSession(
                organisation=admin_dto,
                session=session_response.session
            )

        except AuthApiError as e:
            raise HTTPException(status_code=400, detail=str(e))