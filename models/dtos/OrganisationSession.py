
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.BluStoryAccounts.models.dtos import OrganisationAdmin
class OrganisationSession(BaseModel):
    organisation: OrganisationAdmin
    session: Session