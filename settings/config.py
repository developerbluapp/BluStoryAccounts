
from functools import lru_cache

import os

from blustorymicroservices.BluStoryLicenseHolders.settings import Settings, SupabaseSettings, EmailSettings, RoleSettings
@lru_cache
def get_settings() -> Settings:
    return Settings(
        supabase=SupabaseSettings(
            url=os.environ["SUPABASE_URL"],
            service_role_key=os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        ),
        email=EmailSettings(
            suffix="@blustory.internal"
        ),
        roles=RoleSettings()
    )