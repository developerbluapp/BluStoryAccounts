
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.BluStoryLicenseHolders.models.dtos.LicenseHolder import LicenseHolder
class LicenseHolderSessionResponse(BaseModel):
    licenseholder: LicenseHolder
    session: Session