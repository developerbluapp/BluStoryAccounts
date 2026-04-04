
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.blustory_accounts_auth.models.responses.api.organisations.OrganisationAdminResponse import OrganisationAdminResponse
class OrganisationSessionResponse(BaseModel):
    organisation: OrganisationAdminResponse
    session: Session