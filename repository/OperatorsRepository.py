from http.client import HTTPException
from urllib import response
from uuid import UUID

from fastapi import HTTPException

from blustorymicroservices.BluStoryOperators.models.auth import UserRoles
from blustorymicroservices.BluStoryOperators.models.dtos import \
    AuthOperator, Operator, OperatorSession,Member, Roles
from blustorymicroservices.BluStoryOperators.models.exceptions.operators import UserSignupAlreadyExistsException
from blustorymicroservices.BluStoryOperators.settings.config import \
    get_settings
from blustorymicroservices.BluStoryOperators.settings.Settings import \
    Settings
from blustorymicroservices.BluStoryOperators.models.responses import SupabaseUserResponse
from supabase import Client, create_client
from blustorymicroservices.BluStoryOperators.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.BluStoryOperators.models.exceptions.members import UserAlreadyExistsException
from gotrue.errors import AuthApiError
class OperatorsRepository:
    def __init__(self, client: Client):
        self._client = client

    def _map_supabase_auth_user_to_operator(self, user: SupabaseUserResponse) -> Operator:
        return Operator(
            id=user.id,
            email=user.email,
            phone=user.phone,
            email_confirmed_at=user.email_confirmed_at,
            phone_confirmed_at=user.phone_confirmed_at,
            confirmed_at=user.confirmed_at,
            last_sign_in_at=user.last_sign_in_at,
            app_metadata=user.app_metadata,
            user_metadata=user.user_metadata,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_anonymous=user.is_anonymous
        )

    def signup_operator(self, auth_operator_dto: AuthOperator, username: str) -> OperatorSession:
        try:
                # 1. Sign up user
            role_response = self._client.table("roles").select("*").eq("name", UserRoles.LICENSE_HOLDER).maybe_single().execute()
            roles = Roles(roles=[role_response.data["name"]])
            response = self._client.auth.admin.create_user({
                "email": auth_operator_dto.email,
                "password": auth_operator_dto.password,
                "email_confirm": True,
                "user_metadata": {"avatar_url": "https://picsum.photos/id/237/200/300"},
                "app_metadata": {"roles": roles.model_dump()["roles"]} 
            })
            self._client.table("operators").insert({
                "id": str(response.user.id)
            }).execute()
            self._client.table("user_roles").insert({
                "user_id": response.user.id,
                "role_id": role_response.data["id"]
            }).execute()
                        # 2. Sign in the user to get a session
            session_response = self._client.auth.sign_in_with_password({
                "email": auth_operator_dto.email,
                "password": auth_operator_dto.password
            })
            if "error" in session_response and session_response["error"]:
                raise HTTPException(status_code=400, detail=session_response["error"]["message"])
            operator = self._map_supabase_auth_user_to_operator(SupabaseUserResponse(**response.user.model_dump()))
            return OperatorSession(
                operator=operator,
                session=session_response.session
            )
        except AuthApiError as e:
            if "already been registered" in str(e):
                raise UserSignupAlreadyExistsException(email=auth_operator_dto.email)
            else:
                raise
    def signin_operator(self, auth_operator_dto: AuthOperator) -> OperatorSession:
        try:
            session_response = self._client.auth.sign_in_with_password({
                "email": auth_operator_dto.email,
                "password": auth_operator_dto.password
            })
            if "error" in session_response and session_response["error"]:
                raise HTTPException(status_code=400, detail=session_response["error"]["message"])
            user_response = self._client.auth.get_user(session_response.session.access_token)
            operator = self._map_supabase_auth_user_to_operator(SupabaseUserResponse(**user_response.user.model_dump()))
            return OperatorSession(
                operator=operator,
                session=session_response.session
            )
        except AuthApiError as e:
            raise HTTPException(status_code=400, detail=str(e))
    def get_operator_by_id(self, operator_id: UUID) -> Operator | None:
        response = self._client.auth.admin.get_user_by_id(str(operator_id))
        if not response.user:
            return None
        return self._map_supabase_auth_user_to_operator(SupabaseUserResponse(**response.user.model_dump()))