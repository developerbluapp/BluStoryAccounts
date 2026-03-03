
import datetime
from typing import Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, EmailStr





class SignedupResponse(BaseModel):
    id: UUID
    email: EmailStr | None = None
    phone: str | None = None
    email_confirmed_at: datetime | None = None
    phone_confirmed_at: datetime | None = None
    confirmed_at: datetime | None = None
    last_sign_in_at: datetime | None = None
    app_metadata: dict[str, Any] | None = None
    user_metadata: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    is_anonymous: bool = False
    # model_config = ConfigDict(extra="ignore")
    