

from pydantic import BaseModel


class OperatorSignupRequest(BaseModel):
    email: str
    password: str