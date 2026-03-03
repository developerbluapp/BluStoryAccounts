
from pydantic import BaseModel
from uuid import UUID
class LicenseHolderResponse(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    id: UUID
    email: str
    username: str