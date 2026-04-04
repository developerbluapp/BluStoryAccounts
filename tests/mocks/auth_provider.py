import uuid
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, Union
from sqlalchemy import text

# Gotrue / Supabase Imports
from gotrue.types import User, UserResponse, AuthResponse, Session

# Local Imports
from blustorymicroservices.blustory_accounts_auth.interfaces.AuthProvider import AuthProvider
from blustorymicroservices.blustory_accounts_auth.pgsqlalchemy.SQLAlchemyDatabaseProvider import SQLAlchemyDatabaseProvider

class MockAuthProvider(AuthProvider):
    def __init__(self, db_provider: SQLAlchemyDatabaseProvider):
        self.db = db_provider
        # 📍 REGISTRY: Maps Token -> User Object
        self.users_registry: Dict[str, User] = {}

    def _generate_mock_user_object(
        self, 
        user_id: str, 
        email: str, 
        app_metadata: Dict[str, Any]
    ) -> User:
        """Constructs User object. Ensures organisation_id is present."""
        # 📍 CRITICAL: If no org_id is provided, we generate one, 
        # but in E2E, the service layer should be passing the REAL one from the DB.
        if "organisation_id" not in app_metadata or not app_metadata["organisation_id"]:
            app_metadata["organisation_id"] = str(uuid.uuid4())

        return User(
            id=user_id,
            email=email,
            user_metadata={},
            app_metadata=app_metadata,
            aud="authenticated",
            created_at=str(datetime.now()),
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
        new_user_id = str(uuid.uuid4())
        
        # Sync to local 'auth.users' table so the User FK exists
        self.db.session.execute(
            text("INSERT INTO auth.users (id, email) VALUES (:id, :email)"),
            {"id": new_user_id, "email": email}
        )
        self.db.session.commit()
        
        # Use metadata passed from your Service Layer
        final_metadata = app_metadata or {"roles": ["organisation_admin"]}
        
        mock_user = self._generate_mock_user_object(new_user_id, email, final_metadata)
        
        # 📍 REGISTER
        token = f"mock_tk_{new_user_id}"
        self.users_registry[token] = mock_user
        
        return UserResponse(user=mock_user)

    def sign_in(self, email: str, password: str) -> AuthResponse:
        """Simulates sign-in. If user exists in registry, use that; else create."""
        # Try to find existing user by email in registry
        existing_user = next((u for u in self.users_registry.values() if u.email == email), None)
        
        if existing_user:
            mock_user = existing_user
            user_id = existing_user.id
        else:
            user_id = str(uuid.uuid4())
            mock_user = self._generate_mock_user_object(
                user_id, email, {"roles": ["organisation_admin"]}
            )

        token = f"mock_tk_{user_id}"
        self.users_registry[token] = mock_user
        
        mock_session = Session(
            access_token=token,
            refresh_token="mock_refresh",
            expires_in=3600,
            token_type="bearer",
            user=mock_user
        )
        return AuthResponse(session=mock_session, user=mock_user)

    def get_user_by_token(self, access_token: str) -> UserResponse:
        clean_token = access_token.replace("Bearer ", "").strip()
        user = self.users_registry.get(clean_token)
        
        if not user:
            # Emergency fallback to prevent Pydantic crashes
            user = self._generate_mock_user_object(
                str(uuid.uuid4()), "fallback@test.com", {"roles": ["organisation_admin"]}
            )
            
        return UserResponse(user=user)

    def get_user_by_id(self, user_id: Union[str, UUID]) -> Optional[UserResponse]:
        for user in self.users_registry.values():
            if str(user.id) == str(user_id):
                return UserResponse(user=user)
        return None

    def delete_user(self, user_id: Union[str, UUID]) -> None:
        self.db.session.execute(text("DELETE FROM auth.users WHERE id = :id"), {"id": str(user_id)})
        self.db.session.commit()

    def generate_magic_link(self, email: str, **kwargs) -> str:
        return "http://localhost:8000/verify?token=mock"

    def update_user(self, user_id: Union[str, UUID], password: Optional[str] = None) -> Dict[str, Any]:
        return {"id": str(user_id), "updated": True}