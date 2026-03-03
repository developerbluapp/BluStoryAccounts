
from pydantic import BaseModel
from uuid import UUID
class LicenseHolderResponse(BaseModel):
    id: UUID
    email: str
    username: str