from pydantic import BaseModel

class PatchedStudentResponse(BaseModel):
    id:str
    username: str
    message: str 