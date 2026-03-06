
from pydantic import BaseModel


class AuthOperator(BaseModel):
    email: str
    password: str