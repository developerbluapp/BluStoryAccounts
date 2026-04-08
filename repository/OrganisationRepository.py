from uuid import UUID
from fastapi import HTTPException
from blustorymicroservices.BluStoryAccounts.models.dtos.Organisation import Organisation
from supabase import Client

class OrganisationRepository:
    def __init__(self, client: Client):
        self._client = client

    def get_organisation_by_name(self, organisation_name: str) -> Organisation:
        org_record = self._client.table("organisations").select("*").eq("name", organisation_name).maybe_single().execute()
        if not org_record:
            raise HTTPException(status_code=404, detail=f"Organisation '{organisation_name}' not found")
        data = org_record.data
        return Organisation(id=data["id"], name=data["name"], created_at=data["created_at"])

    def get_organisation_by_id(self, organisation_id: UUID) -> Organisation:
        org_record = self._client.table("organisations").select("*").eq("id", str(organisation_id)).maybe_single().execute()
        if not org_record:
            raise HTTPException(status_code=404, detail="Organisation not found")
        data = org_record.data
        return Organisation(id=data["id"], name=data["name"], created_at=data["created_at"])

    def get_organisation_name_by_id(self, organisation_id: UUID) -> str:
        org_record = self._client.table("organisations").select("name").eq("id", str(organisation_id)).maybe_single().execute()
        if not org_record:
            raise HTTPException(status_code=404, detail="Organisation not found")
        return org_record.data["name"]

    def create_organisation(self, organisation_id: str, organisation_name: str):
        self._client.table("organisations").insert({
            "id": organisation_id,
            "name": organisation_name
        }).execute()
