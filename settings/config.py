
import operator
import os
from functools import lru_cache


from blustorymicroservices.blustory_accounts_auth.settings import (
    EmailSettings, RoleSettings, Settings, SupabaseSettings,OperatorSettings,DeepLinkSettings,InternalClientsSettings,PGSQLSettings)


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
        deep_link = DeepLinkSettings(),
        roles=RoleSettings(),
        operator=OperatorSettings(),
        internal_clients=InternalClientsSettings(),
        pgsqlsettings=PGSQLSettings(database_url=os.environ["PGSQL_URL"])
        
    )