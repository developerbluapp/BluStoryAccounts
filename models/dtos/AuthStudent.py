
from pydantic import BaseModel


class AuthStudent(BaseModel):
    username: str
    password: str