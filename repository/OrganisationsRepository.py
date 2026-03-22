from uuid import UUID, uuid4
from fastapi import HTTPException

from blustorymicroservices.BluStoryAccounts.models.auth import UserRoles
from blustorymicroservices.BluStoryAccounts.models.dtos import (
    AuthOrganisation,
    OrganisationAdmin,
    OrganisationSession,
    Roles,
)
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.CreateOrganisationAdminResponse import (
    CreatedOrganisationAdminResponse,
)
from blustorymicroservices.BluStoryAccounts.providers.interfaces.AuthProvider import (
    AuthProvider,
)
from blustorymicroservices.BluStoryAccounts.providers.interfaces.DatabaseProvider import (
    DatabaseProvider,
)
from blustorymicroservices.BluStoryAccounts.models.responses import (
    SupabaseUserResponse,
)


class OrganisationsRepository:
    def __init__(self, auth_client: AuthProvider, db_client: DatabaseProvider):
        self._db_client = db_client
        self._auth_client = auth_client

    # ----------------------------
    # MAPPERS
    # ----------------------------
    def _map_auth_user_to_organisation(
        self,
        user: SupabaseUserResponse,
        organisation_id: UUID,
        organisation_name: str,
    ) -> OrganisationAdmin:
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
            is_anonymous=user.is_anonymous,
        )

    # ----------------------------
    # HELPERS
    # ----------------------------
    def _get_role(self, role_name: str) -> dict:
        role = self._db_client.select_one(
            "roles",
            {"name": role_name},
        )
        if not role:
            raise HTTPException(
                status_code=500,
                detail=f"Role '{role_name}' not found in database",
            )
        return role

    def get_organisation_name_by_id(self, organisation_id: UUID) -> str:
        org = self._db_client.select_one(
            "organisations",
            {"id": str(organisation_id)},
        )

        if not org:
            raise HTTPException(status_code=404, detail="Organisation not found")

        return org["name"]

    # ----------------------------
    # SIGNUP
    # ----------------------------
    def signup_organisation(
        self,
        auth_organisation_dto: AuthOrganisation,
    ) -> OrganisationSession:

        # 1️⃣ Check if organisation exists
        existing = self._db_client.select_one(
            "organisations",
            {"name": auth_organisation_dto.organisation_name},
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Organisation '{auth_organisation_dto.organisation_name}' already exists",
            )

        # 2️⃣ Get role
        role = self._get_role(UserRoles.ORGANISATION_ADMIN)

        roles = Roles(roles=[role["name"]])
        organisation_id = str(uuid4())

        # 3️⃣ Create auth user
        user = self._auth_client.create_user(
            email=auth_organisation_dto.email,
            password=auth_organisation_dto.password,
            email_confirm=True,
            user_metadata={"avatar_url": "https://picsum.photos/id/237/200/300"},
            app_metadata={
                "organisation_id": organisation_id,
                "roles": roles.model_dump()["roles"],
            },
        )

        # 4️⃣ Create organisation
        self._db_client.insert(
            "organisations",
            {
                "id": organisation_id,
                "name": auth_organisation_dto.organisation_name,
            },
        )

        # 5️⃣ Assign role
        self._db_client.insert(
            "user_roles",
            {
                "user_id": user.user.id,
                "role_id": role["id"],
                "organisation_id": organisation_id,
            },
        )

        # 6️⃣ Sign in
        session = self._auth_client.sign_in(
            email=auth_organisation_dto.email,
            password=auth_organisation_dto.password,
        )
        print(session)

        user_data = self._auth_client.get_user_by_token(session.session.access_token)
        print("Userdo",user_data)

        organisation = self._map_auth_user_to_organisation(
            SupabaseUserResponse(**user_data.user.model_dump()),
            organisation_id=organisation_id,
            organisation_name=auth_organisation_dto.organisation_name,
        )

        return OrganisationSession(
            organisation=organisation,
            session=session.session,
        )

    # ----------------------------
    # SIGNIN
    # ----------------------------
    def signin_organisation(
        self,
        auth_organisation_dto: AuthOrganisation,
    ) -> OrganisationSession:

        role = self._get_role(UserRoles.ORGANISATION_ADMIN)

        # 1️⃣ Sign in
        session = self._auth_client.sign_in(
            email=auth_organisation_dto.email,
            password=auth_organisation_dto.password,
        )

        user_data = self._auth_client.get_user_by_token(session.session.access_token)
        user_id = user_data["id"]

        # 2️⃣ Find organisation via role mapping
        user_role = self._db_client.select_one(
            "user_roles",
            {
                "user_id": str(user_id),
                "role_id": str(role["id"]),
            },
        )

        if not user_role:
            raise HTTPException(
                status_code=400,
                detail="Organisation admin role not assigned",
            )

        organisation_id = user_role["organisation_id"]

        # 3️⃣ Get organisation
        org = self._db_client.select_one(
            "organisations",
            {"id": organisation_id},
        )

        if not org:
            raise HTTPException(
                status_code=400,
                detail="Organisation not found for user",
            )
        
        print(user_data)

        organisation = self._map_auth_user_to_organisation(
            SupabaseUserResponse(**user_data.model_dump()),
            organisation_id=organisation_id,
            organisation_name=org["name"],
        )

        return OrganisationSession(
            organisation=organisation,
            session=session,
        )

    # ----------------------------
    # CREATE ADDITIONAL ADMIN
    # ----------------------------
    def create_and_assign_organisation_admin(
        self,
        email: str,
        password: str,
        organisation_name: str,
    ) -> CreatedOrganisationAdminResponse:

        # 0️⃣ Get organisation
        org = self._db_client.select_one(
            "organisations",
            {"name": organisation_name},
        )

        if not org:
            raise HTTPException(
                status_code=404,
                detail=f"Organisation '{organisation_name}' not found",
            )

        organisation_id = org["id"]

        # 1️⃣ Get role
        role = self._get_role(UserRoles.ORGANISATION_ADMIN)

        roles = Roles(roles=[role["name"]])

        # 2️⃣ Create user
        user = self._auth_client.create_user(
            email=email,
            password=password,
            email_confirm=True,
            user_metadata={"avatar_url": "https://picsum.photos/id/237/200/300"},
            app_metadata={
                "organisation_id": organisation_id,
                "roles": roles.model_dump()["roles"],
            },
        )

        # 3️⃣ Assign role
        self._db_client.insert(
            "user_roles",
            {
                "user_id": user["id"],
                "role_id": role["id"],
                "organisation_id": organisation_id,
            },
        )

        return CreatedOrganisationAdminResponse(
            id=user["id"],
            email=email,
            password=password,
            organisation_id=organisation_id,
        )