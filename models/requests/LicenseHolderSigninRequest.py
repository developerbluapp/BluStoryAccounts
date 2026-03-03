

from pydantic import BaseModel


class LicenseHolderSigninRequest(BaseModel):
    email: str
    password: str