# --- Data models ---

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID

class Member(BaseModel):
    id: UUID
    username: str
    first_name: str