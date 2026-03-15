from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from supabase import Client
from blustorymicroservices.BluStoryOperators.dependencies.clients import get_supabase_client
from blustorymicroservices.BluStoryOperators.models.auth import AuthenticatedOperator, AuthenticatedMember, UserRoles, AuthenticatedOrganisationAdmin

security = HTTPBearer(scheme_name="Bearer", auto_error=False)

async def get_current_organisation_admin(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    supabase: Client = Depends(get_supabase_client),
) -> AuthenticatedOrganisationAdmin:  # or your User model
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

    roles = user.app_metadata.get("roles")
    if UserRoles.ORGANISATION_ADMIN not in roles:
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

    return AuthenticatedOrganisationAdmin(
        id=user.id,
        email=user.email,
        roles=roles,
        aud=user.aud
    )

async def get_current_operator(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    supabase: Client = Depends(get_supabase_client),
) -> AuthenticatedOperator:  # or your User model
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

    roles = user.app_metadata.get("roles")
    if UserRoles.LICENSE_HOLDER not in roles:
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

    return AuthenticatedOperator(
        id=user.id,
        organization_id=user.app_metadata.get("organization_id"),
        email=user.email,
        roles=roles,
        aud=user.aud
    )
async def get_current_member(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    supabase: Client = Depends(get_supabase_client),
) -> AuthenticatedMember:  # or your User model
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

    roles = user.app_metadata.get("roles")
    if UserRoles.STUDENT not in roles:
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

    return AuthenticatedMember(
        id=user.id,
        operator_id=user.app_metadata.get("operator_id"),
        email=user.email,
        roles=roles,
        aud=user.aud
    )