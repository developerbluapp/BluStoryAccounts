from pydantic import BaseModel

class OperatorCountResponse(BaseModel):
    count: int
