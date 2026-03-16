

from pydantic import BaseModel


class OperatorSigninRequest(BaseModel):
    username: str
    password: str