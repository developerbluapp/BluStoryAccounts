

from pydantic import BaseModel


class OrganisationSigninRequest(BaseModel):
    email: str
    password: str