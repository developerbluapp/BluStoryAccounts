import httpx
from blustorymicroservices.blustory_accounts_auth.models.dtos import AuthOperator, OperatorSession, Operator

from blustorymicroservices.blustory_accounts_auth.models.responses.api.operators.CreatedOperatorResponse import CreatedOperatorResponse
from fastapi import HTTPException
from gotrue.errors import AuthApiError
import os
import uuid
import secrets
import string

from blustorymicroservices.blustory_accounts_auth.providers.interfaces.AuthProvider import AuthProvider

SPRING_DB_URL = os.getenv("SPRING_DB_SERVICE_URL", "http://localhost:8081")

class OperatorAuthService:
    def __init__(self, auth_client: AuthProvider):
        self._auth_client = auth_client

    def _create_random_username(self, length : int=20) -> str:
        alphabet = string.ascii_lowercase + string.digits
        username = ''.join(secrets.choice(alphabet) for _ in range(length))
        return username

    def signup_operator(self, org_token: str) -> CreatedOperatorResponse:
        try:
            # Validate token with Supabase and extract organisation claims
            user_data = self._auth_client.get_user_by_token(org_token)
            if not user_data:
                raise HTTPException(status_code=401, detail="Invalid token")
                
            org_id = user_data.user.app_metadata.get("organisation_id")
            if not org_id:
                raise HTTPException(status_code=403, detail="Not linked to an organisation")

            username = self._create_random_username()
            password = "generatedpassword123" # in real systems generate random or email reset
            fake_email = f"{username}@temp.com"
            operator_id = str(uuid.uuid4())

            # 1. Create User in Supabase Auth
            user = self._auth_client.create_user(
                email=fake_email,
                password=password,
                email_confirm=True,
                app_metadata={
                    "organisation_id": org_id,
                    "roles": ["operator"],
                },
            )

            # 2. Persist Operator to DB App
            payload = {
                "id": str(user.user.id),
                "username": username,
                "organisation": {
                    "id": org_id
                }
            }
            resp = httpx.post(f"{SPRING_DB_URL}/internal/operators", json=payload)
            
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to persist operator in DB.")

            return CreatedOperatorResponse(
                id=user.user.id,
                username=username,
                password=password,
                organisation_id=uuid.UUID(org_id)
            )

        except AuthApiError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def signin_operator(self, auth_operator_dto: AuthOperator) -> OperatorSession:
        try:
            resp = httpx.get(f"{SPRING_DB_URL}/internal/operators", params={"username": auth_operator_dto.username})
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="Operator not found in DB.")
                
            operator_data = resp.json()
            user_auth = self._auth_client.get_user_by_id(operator_data["id"])
            if not user_auth:
                raise HTTPException(status_code=404, detail="Operator Auth missing.")
                
            email = user_auth.user.email

            session = self._auth_client.sign_in(
                email=email,
                password=auth_operator_dto.password,
            )

            operator = Operator(
                id=operator_data["id"],
                username=operator_data["username"],
                email=email
            )
            return OperatorSession(operator=operator, session=session.session)
        except AuthApiError as e:
            raise HTTPException(status_code=400, detail=str(e))