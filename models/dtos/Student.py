# --- Data models ---

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID

class Student(BaseModel):
    id: UUID
    username: str
 