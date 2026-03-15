
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.BluStoryOperators.models.dtos import Organisation
class OrganisationSession(BaseModel):
    organisation: Organisation
    session: Session