
from pydantic import BaseModel
from uuid import UUID
class OrganisationResponse(BaseModel):
    id: UUID
    email: str
    organisation_id:UUID
    organisation_name: str
