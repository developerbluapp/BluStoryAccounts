# --- API schemas ---

from pydantic import BaseModel, EmailStr


class CreateOperatorRequest(BaseModel):
    email: EmailStr
