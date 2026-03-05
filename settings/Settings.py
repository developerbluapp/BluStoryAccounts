from typing import ClassVar

from pydantic import BaseModel


class RoleSettings(BaseModel):
    license_holder: ClassVar[str] = "license_holder"
    member: ClassVar[str] = "member"
    parent: ClassVar[str] = "parent"

class EmailSettings(BaseModel):
    suffix: ClassVar[str] = "@blustory.internal"
    max_length: ClassVar[int] = 254

class SupabaseSettings(BaseModel):
    url: str
    service_role_key: str

class DeepLinkSettings(BaseModel):
    scheme: ClassVar[str] = "com.pallondomus.blustoryapp"
    callback: ClassVar[str] = "://auth/callback"
    url: ClassVar[str] = scheme + callback

class PinSettings(BaseModel):
    secret: str

class Settings(BaseModel):
    supabase: SupabaseSettings
    email: ClassVar[type[EmailSettings]] = EmailSettings  
    roles: ClassVar[type[RoleSettings]] = RoleSettings    
    deeplink: ClassVar[type[DeepLinkSettings]] = DeepLinkSettings 
    pin: PinSettings

    model_config = {"env_file": ".env", "extra": "allow"}