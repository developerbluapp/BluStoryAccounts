
from pydantic import BaseModel


class AuthLicenseHolder(BaseModel):
    email: str
    password: str