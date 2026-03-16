
from uuid import UUID

from pydantic import BaseModel



class CreatedOrganisationAdminResponse(BaseModel):
    id: UUID
    email: str
    password: str
    organisation_id: UUID



