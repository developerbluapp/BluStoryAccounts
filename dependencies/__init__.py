# dependencies/__init__.py — single import surface for routes
from .clients import get_supabase_client
from .repositories import get_user_repository
from .services import get_user_service, get_auth_service
from .auth import get_current_user