# --- API schemas ---

from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    username: str
    first_name: str