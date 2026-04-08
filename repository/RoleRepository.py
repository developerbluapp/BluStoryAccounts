from fastapi import HTTPException
from supabase import Client

class RoleRepository:
    def __init__(self, client: Client):
        self._client = client

    def get_role_id(self, role_name: str) -> str:
        role_response = self._client.table("roles").select("id").eq("name", role_name).maybe_single().execute()
        if not role_response or not role_response.data:
            raise HTTPException(status_code=500, detail=f"Role '{role_name}' not found in database")
        return role_response.data["id"]
