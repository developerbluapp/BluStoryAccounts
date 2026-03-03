

from pydantic import BaseModel


class StudentSigninRequest(BaseModel):
    username: str
    password: str