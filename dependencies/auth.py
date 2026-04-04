from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from supabase import Client
from blustorymicroservices.blustory_accounts_auth.dependencies.externalclients import get_auth_provider
from blustorymicroservices.blustory_accounts_auth.models.auth import AuthenticatedOperator, AuthenticatedMember, UserRoles, AuthenticatedOrganisationAdmin
from blustorymicroservices.blustory_accounts_auth.providers.interfaces.AuthProvider import AuthProvider

security = HTTPBearer(scheme_name="Bearer", auto_error=False)

def get_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Dependency that returns just the token string (without "Bearer " prefix).
    Raises 401 if missing/invalid format.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials   # this is the actual token

async def get_current_organisation_admin(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_client: AuthProvider = Depends(get_auth_provider),
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
    auth_response = auth_client.get_user_by_token(token)

    if not auth_response.user:
        raise ValueError("No user in response")

    user = auth_response.user

    roles = user.app_metadata.get("roles")

    if UserRoles.ORGANISATION_ADMIN not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have the required role.",
        )


    return AuthenticatedOrganisationAdmin(
        id=user.id,
        organisation_id=user.app_metadata.get("organisation_id"),
        email=user.email,
        roles=roles,
        aud=user.aud
    )

async def get_current_operator(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_client: AuthProvider = Depends(get_auth_provider),
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
    auth_response = auth_client.get_user_by_token(token)

    if not auth_response.user:
        raise ValueError("No user in response")

    user = auth_response.user

    roles = user.app_metadata.get("roles")
    if UserRoles.OPERATOR not in roles:
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
        organisation_id=user.app_metadata.get("organisation_id"),
        email=user.email,
        roles=roles,
        aud=user.aud
    )
async def get_current_member(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_client: AuthProvider = Depends(get_auth_provider),
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
    auth_response = auth_client.get_user_by_token(token)

    if not auth_response.user:
        raise ValueError("No user in response")

    user = auth_response.user

    roles = user.app_metadata.get("roles")
    if UserRoles.STUDENT not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have the required role.",
        )


    return AuthenticatedMember(
        id=user.id,
        operator_id=user.app_metadata.get("operator_id"),
        email=user.email,
        roles=roles,
        aud=user.aud
    )