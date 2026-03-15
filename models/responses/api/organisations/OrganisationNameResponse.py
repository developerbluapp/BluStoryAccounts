from uuid import UUID
from pydantic import BaseModel
class OrganisationNameResponse(BaseModel):
    id: UUID
    organisation_name: str