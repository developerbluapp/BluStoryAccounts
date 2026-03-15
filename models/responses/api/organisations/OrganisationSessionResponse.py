
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.BluStoryOperators.models.responses.api.organisations.OrganisationResponse import OrganisationResponse
class OrganisationSessionResponse(BaseModel):
    organisation: OrganisationResponse
    session: Session