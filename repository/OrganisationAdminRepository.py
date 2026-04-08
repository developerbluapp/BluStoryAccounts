from uuid import UUID
from typing import Any
from fastapi import HTTPException
from blustorymicroservices.BluStoryAccounts.models.auth import UserRoles
from blustorymicroservices.BluStoryAccounts.models.dtos import OrganisationAdmin, Roles
from blustorymicroservices.BluStoryAccounts.models.responses import SupabaseUserResponse
from supabase import Client

class OrganisationAdminRepository:
    def __init__(self, client: Client):
        self._client = client

    def map_user_to_admin(self, user: SupabaseUserResponse, organisation_id: UUID, organisation_name: str) -> OrganisationAdmin:
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

    def get_role_id(self, role_name: str) -> str:
        role_response = self._client.table("roles").select("id").eq("name", role_name).maybe_single().execute()
        if not role_response:
            raise HTTPException(status_code=500, detail=f"Role '{role_name}' not found in database")
        return role_response.data["id"]

    def assign_role(self, user_id: UUID, role_id: str, organisation_id: str):
        self._client.table("user_roles").insert({
            "user_id": str(user_id),
            "role_id": role_id,
            "organisation_id": organisation_id
        }).execute()

    def link_to_org(self, user_id: UUID, organisation_id: str):
        self._client.table("org_admin").insert({
            "id": str(user_id),
            "organisation_id": organisation_id
        }).execute()

    def get_admin_organisation_id(self, user_id: UUID) -> str:
        role_id = self.get_role_id(UserRoles.ORGANISATION_ADMIN)
        user_roles_resp = self._client.table("user_roles") \
            .select("organisation_id") \
            .eq("user_id", str(user_id)) \
            .eq("role_id", str(role_id)) \
            .maybe_single() \
            .execute()

        if not user_roles_resp:
            raise HTTPException(status_code=400, detail="OrganisationAdmin admin role not assigned")
        
        return user_roles_resp.data["organisation_id"]
