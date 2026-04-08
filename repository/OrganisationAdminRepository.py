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

    def link_to_org(self, user_id: UUID, organisation_id: str):
        self._client.table("org_admin").insert({
            "id": str(user_id),
            "organisation_id": organisation_id
        }).execute()
