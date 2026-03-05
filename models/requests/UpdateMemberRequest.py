from pydantic import BaseModel, EmailStr

class UpdateMemberRequest(BaseModel):
    username: str