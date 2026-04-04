import httpx
from pydantic import EmailStr
from uuid import UUID, uuid4
from blustorymicroservices.blustory_accounts_auth.models.dtos import \
    AuthOrganisation, OrganisationSession, OrganisationAdmin

from fastapi import HTTPException
from gotrue.errors import AuthApiError
import os
import datetime

from blustorymicroservices.blustory_accounts_auth.providers.interfaces.AuthProvider import AuthProvider

SPRING_DB_URL = os.getenv("SPRING_DB_SERVICE_URL", "http://localhost:8081")

class OrganisationAuthService:
    def __init__(self, auth_client: AuthProvider):
        self._auth_client = auth_client

    def signup_organisation(self, auth_organisation_dto: AuthOrganisation) -> OrganisationSession:
        try:
            # 1. Create auth user in Supabase
            organisation_id = str(uuid4())
            user = self._auth_client.create_user(
                email=auth_organisation_dto.email,
                password=auth_organisation_dto.password,
                email_confirm=True,
                user_metadata={"avatar_url": "https://picsum.photos/id/237/200/300"},
                app_metadata={
                    "organisation_id": organisation_id,
                    "roles": ["organisation_admin"],
                },
            )

            # 2. Tell Spring DB Microservice to create the Organisation record
            payload = {
                "id": organisation_id,
                "name": auth_organisation_dto.organisation_name
            }
            resp = httpx.post(f"{SPRING_DB_URL}/internal/organisations", json=payload)
            if resp.status_code != 200:
                # In a robust system, we would rollback Supabase creation here
                raise HTTPException(status_code=500, detail="Failed to persist Organisation in DB Layer.")
            
            # 3. Sign in to get session
            session = self._auth_client.sign_in(
                email=auth_organisation_dto.email,
                password=auth_organisation_dto.password,
            )

            org_admin = OrganisationAdmin(
                id=user.user.id,
                organisation_id=UUID(organisation_id),
                organisation_name=auth_organisation_dto.organisation_name,
                email=auth_organisation_dto.email,
                created_at=datetime.datetime.now()
            )

            return OrganisationSession(
                organisation=org_admin,
                session=session.session,
            )

        except AuthApiError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def signin_organisation(self, auth_organisation_dto: AuthOrganisation) -> OrganisationSession:
        try:
            # 1. Sign in 
            session = self._auth_client.sign_in(
                email=auth_organisation_dto.email,
                password=auth_organisation_dto.password,
            )
            
            user_data = self._auth_client.get_user_by_token(session.session.access_token)
            
            # Use metadata to fetch from DB
            app_metadata = user_data.user.app_metadata
            organisation_id = app_metadata.get("organisation_id")
            
            if not organisation_id:
                raise HTTPException(status_code=400, detail="No organisation bound to user.")

            # 2. Get Organisation details from DB Microservice
            resp = httpx.get(f"{SPRING_DB_URL}/internal/organisations/{organisation_id}")
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="Organisation DB record missing.")
                
            org_data = resp.json()

            org_admin = OrganisationAdmin(
                id=user_data.user.id,
                organisation_id=UUID(organisation_id),
                organisation_name=org_data["name"],
                email=auth_organisation_dto.email,
                created_at=datetime.datetime.now()
            )

            return OrganisationSession(
                organisation=org_admin,
                session=session.session,
            )

        except AuthApiError as e:
             raise HTTPException(status_code=400, detail=str(e))