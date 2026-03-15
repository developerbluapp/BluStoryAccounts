

from pydantic import BaseModel

class OrganisationSignupRequest(BaseModel):
    organisation_name: str
    email: str
    password: str