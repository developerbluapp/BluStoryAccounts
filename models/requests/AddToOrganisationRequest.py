from pydantic import BaseModel


class AddToOrganisationRequest(BaseModel):
    email: str