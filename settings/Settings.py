from typing import ClassVar

from pydantic import BaseModel


class RoleSettings(BaseModel):
    license_holder: ClassVar[str] = "license_holder"
    student: ClassVar[str] = "student"
    parent: ClassVar[str] = "parent"

class EmailSettings(BaseModel):
    suffix: ClassVar[str] = "@blustory.internal"
    max_length: ClassVar[int] = 254

class SupabaseSettings(BaseModel):
    url: str
    service_role_key: str

class Settings(BaseModel):
    supabase: SupabaseSettings
    email: ClassVar[type[EmailSettings]] = EmailSettings  
    roles: ClassVar[type[RoleSettings]] = RoleSettings    

    model_config = {"env_file": ".env", "extra": "allow"}