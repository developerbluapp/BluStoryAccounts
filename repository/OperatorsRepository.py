from http.client import HTTPException
from urllib import response
from uuid import UUID, uuid4

from fastapi import HTTPException

from blustorymicroservices.BluStoryAccounts.clients.api.OrganisationClient import OrganisationClient
from blustorymicroservices.BluStoryAccounts.models.auth import UserRoles
from blustorymicroservices.BluStoryAccounts.models.dtos import \
    AuthOperator, Operator, OperatorSession,Member, Roles
from blustorymicroservices.BluStoryAccounts.models.dtos.OrganisationAdmin import OrganisationAdmin
from blustorymicroservices.BluStoryAccounts.models.exceptions.operators import UserSignupAlreadyExistsException
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.CreatedOperatorResponse import CreatedOperatorResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.ResetOperatorPasswordResponse import ResetOperatorPasswordResponse
from blustorymicroservices.BluStoryAccounts.settings.config import \
    get_settings
from blustorymicroservices.BluStoryAccounts.settings.Settings import \
    Settings
from blustorymicroservices.BluStoryAccounts.models.responses import SupabaseUserResponse
from supabase import Client, create_client
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.BluStoryAccounts.models.exceptions.members import UserAlreadyExistsException
from gotrue.errors import AuthApiError
class OperatorsRepository:
    def __init__(self, auth_client: Client,db_client : Client):
        self._db_client =  db_client 
        self._auth_client = auth_client


    def _map_supabase_auth_user_to_operator(self, user: SupabaseUserResponse, username: str) -> Operator:
        return Operator(
            id=user.id,
            email=user.email,
            phone=user.phone,
            username=username,
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
    def _map_supabase_auth_user_to_organisation(self, user: SupabaseUserResponse,organisation_name: str) -> OrganisationAdmin:
        return OrganisationAdmin(
            id=user.id,
            email=user.email,
            organisation_name=organisation_name,
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

    def create_operator(self,username: str,password:str,fake_email:str,organisation_name: str,organisation_id: UUID) -> CreatedOperatorResponse:
        
        try:
  
            role_response = self._db_client.table("roles").select("*").eq("name", UserRoles.OPERATOR).maybe_single().execute()
            

            roles = Roles(roles=[role_response.data["name"]])
            response = self._auth_client.auth.admin.create_user({
                "email": fake_email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"avatar_url": "https://picsum.photos/id/237/200/300"},
                "app_metadata": {"roles": roles.model_dump()["roles"],
                                "organisation_id": str(organisation_id) } 
            })
            self._db_client.table("operators").insert({
            "id": str(response.user.id),
            "username": username,
            "organisation_id": str(organisation_id)
            }).execute()
            self._db_client.table("user_roles").insert({
                "user_id": response.user.id,
                "role_id": role_response.data["id"],
                "organisation_id": str(organisation_id)
            }).execute()
            
            if not response:
                raise HTTPException(status_code=500, detail="Failed to insert member record")

            return CreatedOperatorResponse(
                id=response.user.id,
                username=username,
                password=password,
                organisation_id=organisation_id
            )
        
        except AuthApiError as e:
            if "already been registered" in str(e):
                raise UserAlreadyExistsException(username=username)
            else:
                raise
    
    def signin_operator(self, auth_operator_dto: AuthOperator) -> OperatorSession:
        try:
            operators_response = self._db_client.table("operators").select("id").eq("username", auth_operator_dto.username).maybe_single().execute()
            if not operators_response:
                raise HTTPException(status_code=404, detail="Operator not found.")
            operator_id = operators_response.data["id"]
            user_response = self._auth_client.auth.admin.get_user_by_id(operator_id)
            email = user_response.user.email
            
            session_response = self._auth_client.auth.sign_in_with_password({
                "email": email,
                "password": auth_operator_dto.password
            })

            if "error" in session_response and session_response["error"]:
                raise HTTPException(status_code=400, detail=session_response["error"]["message"])
            user_response = self._auth_client.auth.get_user(session_response.session.access_token)
            operator = self._map_supabase_auth_user_to_operator(SupabaseUserResponse(**user_response.user.model_dump()),username=auth_operator_dto.username)
            return OperatorSession(
                operator=operator,
                session=session_response.session
            )
        except AuthApiError as e:
            raise HTTPException(status_code=400, detail=str(e))
    def get_operator_by_id(self, operator_id: UUID) -> Operator | None:
        response = self._auth_client.auth.admin.get_user_by_id(str(operator_id))
        if not response.user:
            return None
        operators_response = self._db_client.table("operators").select("username").eq("id", operator_id).maybe_single().execute()
        username = operators_response.data["username"]
        
        return self._map_supabase_auth_user_to_operator(SupabaseUserResponse(**response.user.model_dump()),username=username)
    def get_operators_by_organisation(self, organisation_id: UUID) -> list[Operator]:
        operators_response = self._db_client.table("operators").select("*").eq("organisation_id", str(organisation_id)).execute()
        operators = []
        print(operators_response.data,"operators response data in repo",organisation_id)
        for operator_record in operators_response.data:
            user_response = self._auth_client.auth.admin.get_user_by_id(operator_record["id"])
            if user_response.user:
                username = operator_record["username"]
                operator = self._map_supabase_auth_user_to_operator(SupabaseUserResponse(**user_response.user.model_dump()),username=username)
                operators.append(operator)
        return operators
    def reset_password(self, organisation_id: UUID, operator_id: UUID, new_password: str) -> ResetOperatorPasswordResponse:
        # Reset password using the user's ID
        operators_response = self._db_client.table("operators").select("*").eq("organisation_id", str(organisation_id)).eq("id", str(operator_id)).maybe_single().execute()
        if not operators_response:
            raise HTTPException(status_code=404, detail="Operator not found or not apart of this organisation.")
        response = self._auth_client.auth.admin.update_user_by_id(
            uid=str(operator_id),
            attributes={"password": new_password}
        )
        return ResetOperatorPasswordResponse(
            id=response.user.id,
            username=operators_response.data["username"],
            password=new_password,
            organisation_id=organisation_id)