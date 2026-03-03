

from pydantic import BaseModel


class LicenseHolderSignupRequest(BaseModel):
    email: str
    password: str