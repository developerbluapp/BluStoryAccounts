
from pydantic import BaseModel


class CreateUserResponse(BaseModel):
    id: str
    email: str
    