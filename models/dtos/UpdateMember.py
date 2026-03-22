
from pydantic import BaseModel


class UpdateMember(BaseModel):
    username:str | None = None
    first_name: str | None = None