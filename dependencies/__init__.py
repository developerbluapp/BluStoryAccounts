# dependencies/__init__.py — single import surface for routes
from .clients import get_supabase_client
from .repositories import  get_student_repository,get_license_holder_repository
from .services import get_student_service, get_auth_service,get_license_holder_service
from .auth import get_current_user
