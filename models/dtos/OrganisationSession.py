
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.blustory_accounts_auth.models.dtos import OrganisationAdmin
class OrganisationSession(BaseModel):
    organisation: OrganisationAdmin
    session: Session