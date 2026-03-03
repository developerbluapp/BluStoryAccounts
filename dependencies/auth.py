from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from supabase import Client
from blustorymicroservices.BluStoryLicenseHolders.dependencies.clients import get_supabase_client
from blustorymicroservices.BluStoryLicenseHolders.models.auth import AuthenticatedLicenseHolder, UserRoles

security = HTTPBearer(scheme_name="Bearer", auto_error=False)

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    supabase: Client = Depends(get_supabase_client),
) -> AuthenticatedLicenseHolder:  # or your User model
    """
    Dependency: extracts & verifies Supabase JWT from Authorization: Bearer <token>
    Returns user data if valid, raises 401 otherwise
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    # This verifies signature, expiration, audience, etc.
    auth_response = supabase.auth.get_user(token)

    if not auth_response.user:
        raise ValueError("No user in response")

    user = auth_response.user

    role = user.app_metadata.get("role")
    if role != UserRoles.LICENSE_HOLDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have the required role.",
        )

    # Optional: you can fetch extra profile data from public.profiles
    # profile = (
    #     supabase.table("profiles")
    #     .select("*")
    #     .eq("id", user.id)
    #     .single()
    #     .execute()
    # ).data

    return AuthenticatedLicenseHolder(
        id=user.id,
        email=user.email,
        role=user.app_metadata.get("role"),
        aud=user.aud
    )
