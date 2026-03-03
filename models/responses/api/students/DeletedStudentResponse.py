from pydantic import BaseModel
class DeletedStudentResponse(BaseModel):
    id: int
    username: str
    message: str
