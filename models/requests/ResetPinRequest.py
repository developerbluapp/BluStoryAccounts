

from pydantic import BaseModel


class ResetPinRequest(BaseModel):
    member_id:str