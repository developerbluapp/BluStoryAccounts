from pydantic import BaseModel, EmailStr

class UpdateStudentRequest(BaseModel):
    username: str