

from pydantic import BaseModel


class MemberSigninRequest(BaseModel):
    username: str
    password: str