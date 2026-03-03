
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.BluStoryLicenseHolders.models.dtos import LicenseHolder
class LicenseHolderSession(BaseModel):
    licenseholder: LicenseHolder
    session: Session