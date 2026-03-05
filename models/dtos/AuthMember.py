
from pydantic import BaseModel


class AuthMember(BaseModel):
    username: str
    password: str