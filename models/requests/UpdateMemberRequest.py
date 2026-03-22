from pydantic import BaseModel, EmailStr

class UpdateMemberRequest(BaseModel):
    username: str | None = None
    first_name: str | None = None