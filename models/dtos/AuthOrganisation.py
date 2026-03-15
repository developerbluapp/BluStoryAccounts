
from pydantic import BaseModel


class AuthOrganisation(BaseModel):
    email: str
    password: str
    organisation_name: str