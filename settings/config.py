
import os
from functools import lru_cache

from blustorymicroservices.BluStoryOperators.settings import (
    EmailSettings, RoleSettings, Settings, SupabaseSettings,PinSettings)


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
        roles=RoleSettings(),
        pin=PinSettings(
            secret=os.environ["PIN_SECRET"]
        )
    )