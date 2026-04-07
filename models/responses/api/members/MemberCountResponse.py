from pydantic import BaseModel

class MemberCountResponse(BaseModel):
    count: int
