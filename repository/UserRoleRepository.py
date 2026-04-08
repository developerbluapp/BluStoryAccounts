from uuid import UUID
from supabase import Client

class UserRoleRepository:
    def __init__(self, client: Client):
        self._client = client

    def assign_role(self, user_id: UUID, role_id: str, organisation_id: str):
        self._client.table("user_roles").insert({
            "user_id": str(user_id),
            "role_id": role_id,
            "organisation_id": organisation_id
        }).execute()

    def get_organisation_id_by_user_and_role(self, user_id: UUID, role_id: str) -> str | None:
        user_roles_resp = self._client.table("user_roles") \
            .select("organisation_id") \
            .eq("user_id", str(user_id)) \
            .eq("role_id", str(role_id)) \
            .maybe_single() \
            .execute()

        if not user_roles_resp or not user_roles_resp.data:
            return None
        
        return user_roles_resp.data["organisation_id"]
