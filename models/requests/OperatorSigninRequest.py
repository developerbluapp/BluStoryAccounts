

from pydantic import BaseModel


class OperatorSigninRequest(BaseModel):
    email: str
    password: str