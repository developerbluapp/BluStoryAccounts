
from pydantic import BaseModel


class AuthOperator(BaseModel):
    username: str
    password: str