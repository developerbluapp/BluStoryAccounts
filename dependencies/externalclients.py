
from blustorymicroservices.BluStoryAccounts.providers.interfaces.AuthProvider import AuthProvider
from blustorymicroservices.BluStoryAccounts.providers.interfaces.DatabaseProvider import DatabaseProvider
from blustorymicroservices.BluStoryAccounts.providers.pgsqlalchemy.SQLAlchemyDatabaseProvider import SQLAlchemyDatabaseProvider
from blustorymicroservices.BluStoryAccounts.providers.supabase.SupabaseAuthProvider import SupabaseAuthProvider
from blustorymicroservices.BluStoryAccounts.providers.supabase.SupabaseDatabaseProvider import SupabaseDatabaseProvider
from blustorymicroservices.BluStoryAccounts.repository.MembersRepository import MembersRepository
from blustorymicroservices.BluStoryAccounts.settings import Settings
from blustorymicroservices.BluStoryAccounts.settings.config import \
    get_settings
from fastapi import Depends
from supabase import Client, create_client
from blustorymicroservices.BluStoryAccounts.clients.api.OrganisationClient import OrganisationClient
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/mydatabase"

def get_supabase_client(
    settings: Settings = Depends(get_settings)
) -> Client:
    """Single shared client — service role key = admin powers"""
    return create_client(
        supabase_url=settings.supabase.url,
        supabase_key=settings.supabase.service_role_key
    )

def get_pgsql_client(settings: Settings = Depends(get_settings)):
    """Provide a single SQLAlchemy session per request, auto-closed by FastAPI"""
    
    # Create engine
    engine = create_engine(settings.pgsqlsettings.database_url, future=True)
    
    # Create session factory
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    
    # Create a session
    session = SessionLocal()
    
    try:
        yield session  # yields the session to the endpoint
    finally:
        session.close()  # ensures the session is closed after the request


def get_auth_provider(
    client: Client = Depends(get_supabase_client)
) -> AuthProvider:
    return SupabaseAuthProvider(client)


def get_db_provider(
    client: Client = Depends(get_supabase_client)
) -> DatabaseProvider:
    return SupabaseDatabaseProvider(client)

def get_regression_db_provider(
    client: Session = Depends(get_pgsql_client)
) -> SQLAlchemyDatabaseProvider:
    """Provide SQLAlchemyDatabaseProvider using the live session"""
    
    # Create metadata object (for dynamic table reflection)
    metadata = MetaData()
    
    # Return the provider
    return SQLAlchemyDatabaseProvider(session=client, metadata=metadata)