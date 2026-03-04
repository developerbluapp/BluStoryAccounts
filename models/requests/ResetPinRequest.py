

from pydantic import BaseModel


class ResetPinRequest(BaseModel):
    student_id:str