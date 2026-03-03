
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.licenseholders.LicenseHolderResponse import LicenseHolderResponse
class LicenseHolderSessionResponse(BaseModel):
    licenseholder: LicenseHolderResponse
    session: Session