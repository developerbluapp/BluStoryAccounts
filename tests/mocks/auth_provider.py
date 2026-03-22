import uuid
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, Union
from sqlalchemy import text

# Gotrue / Supabase Imports
from gotrue.types import User, UserResponse, AuthResponse, Session

# Local Imports
from blustorymicroservices.BluStoryAccounts.providers.interfaces.AuthProvider import AuthProvider
from blustorymicroservices.BluStoryAccounts.providers.pgsqlalchemy.SQLAlchemyDatabaseProvider import SQLAlchemyDatabaseProvider

class MockAuthProvider(AuthProvider):
    def __init__(self, db_provider: SQLAlchemyDatabaseProvider):
        self.db = db_provider

    def _generate_mock_user(self, user_id: str, email: str, user_metadata: Optional[Dict] = None) -> User:
        """Helper to create a User object that satisfies Pydantic validation requirements."""
        return User(
            id=user_id,
            email=email,
            user_metadata=user_metadata or {},
            app_metadata={"roles":["organisation_admin"]},        # Required field
            aud="authenticated",    # Required field
            created_at=str(datetime.now()), # Required field
            updated_at=str(datetime.now())
        )

    def create_user(
        self, 
        email: str, 
        password: str, 
        email_confirm: bool = True, 
        user_metadata: Optional[Dict] = None, 
        app_metadata: Optional[Dict] = None
    ) -> UserResponse:
        new_id = str(uuid.uuid4())
        
        # 1. Sync to local 'auth.users' table to satisfy Foreign Key constraints
        self.db.insert("auth.users", {"id": new_id, "email": email})
        self.db.session.commit()
        
        # 2. Return a valid UserResponse object
        mock_user = self._generate_mock_user(new_id, email, user_metadata)
        return UserResponse(user=mock_user)

    def sign_in(self, email: str, password: str) -> AuthResponse:
        user_id = str(uuid.uuid4())
        mock_user = self._generate_mock_user(user_id, email)
        
        # 3. Create a valid Session object (required fields included)
        mock_session = Session(
            access_token=f"mock_tk_{user_id}",
            refresh_token="mock_refresh_token",
            expires_in=3600,
            token_type="bearer",
            user=mock_user
        )
        
        return AuthResponse(session=mock_session, user=mock_user)

    def get_user_by_token(self, access_token: str) -> UserResponse:
        # Extract ID from our mock token format
        user_id = access_token.replace("mock_tk_", "")
        mock_user = self._generate_mock_user(user_id, "test@test.com")
        return UserResponse(user=mock_user)

    def get_user_by_id(self, user_id: Union[str, UUID]) -> Optional[UserResponse]:
        mock_user = self._generate_mock_user(str(user_id), "test@test.com")
        return UserResponse(user=mock_user)

    def delete_user(self, user_id: Union[str, UUID]) -> None:
        self.db.session.execute(
            text("DELETE FROM auth.users WHERE id = :id"), 
            {"id": str(user_id)}
        )
        self.db.session.commit()

    def generate_magic_link(self, email: str, **kwargs) -> str:
        return "http://localhost:8000/verify?token=mock_magic_link"

    def update_user(self, user_id: Union[str, UUID], password: Optional[str] = None) -> Dict[str, Any]:
        # Simple mock return to satisfy the interface if you added this method
        return {"id": str(user_id), "updated": True}