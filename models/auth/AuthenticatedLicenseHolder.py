from pydantic import BaseModel
from uuid import UUID


class AuthenticatedLicenseHolder(BaseModel):
    id :UUID
    email: str
    role: str
    aud: str
