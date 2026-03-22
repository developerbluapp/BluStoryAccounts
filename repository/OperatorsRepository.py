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
from blustorymicroservices.BluStoryAccounts.providers.interfaces.AuthProvider import AuthProvider
from blustorymicroservices.BluStoryAccounts.providers.interfaces.DatabaseProvider import DatabaseProvider
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
    def __init__(self, auth_client: AuthProvider, db_client: DatabaseProvider):
        self._db_client = db_client
        self._auth_client = auth_client

    def _map_supabase_auth_user_to_operator(
        self, user: SupabaseUserResponse, username: str
    ) -> Operator:
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
            is_anonymous=user.is_anonymous,
        )

    def create_operator(
        self,
        username: str,
        password: str,
        fake_email: str,
        organisation_name: str,
        organisation_id: UUID,
    ) -> CreatedOperatorResponse:

        # 1. Get role
        role = self._db_client.select_one(
            table="roles",
            filters={"name": UserRoles.OPERATOR},
        )

        if not role:
            raise HTTPException(status_code=500, detail="Role not found")

        roles = Roles(roles=[role["name"]])

        try:
            # 2. Create auth user
            user = self._auth_client.create_user(
                email=fake_email,
                password=password,
                email_confirm=True,
                user_metadata={"avatar_url": "https://picsum.photos/id/237/200/300"},
                app_metadata={
                    "roles": roles.model_dump()["roles"],
                    "organisation_id": str(organisation_id),
                },
            )

            # 3. Insert operator
            self._db_client.insert(
                "operators",
                {
                    "id": user["id"],
                    "username": username,
                    "organisation_id": str(organisation_id),
                },
            )

            # 4. Insert user role
            self._db_client.insert(
                "user_roles",
                {
                    "user_id": user["id"],
                    "role_id": role["id"],
                    "organisation_id": str(organisation_id),
                },
            )

            return CreatedOperatorResponse(
                id=user["id"],
                username=username,
                password=password,
                organisation_id=organisation_id,
            )

        except AuthApiError as e:
            if "already been registered" in str(e):
                raise UserAlreadyExistsException(username=username)
            raise

    def signin_operator(self, auth_operator_dto: AuthOperator) -> OperatorSession:
        try:
            operator_record = self._db_client.select_one(
                table="operators",
                filters={"username": auth_operator_dto.username},
            )

            if not operator_record:
                raise HTTPException(status_code=404, detail="Operator not found.")

            operator_id = operator_record["id"]

            user = self._auth_client.get_user_by_id(operator_id)
            email = user.user.email

            session = self._auth_client.sign_in(
                email=email,
                password=auth_operator_dto.password,
            )

            user_data = self._auth_client.get_user_by_token(session.session.access_token)

            operator = self._map_supabase_auth_user_to_operator(
                SupabaseUserResponse(**user_data.user.model_dump()),
                username=auth_operator_dto.username,
            )
            

            return OperatorSession(operator=operator, session=session.session)

        except AuthApiError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def get_operator_by_id(self, operator_id: UUID) -> Operator | None:
        user = self._auth_client.get_user_by_id(str(operator_id))
        print("HELO",user)
        if not user:
            return None

        operator_record = self._db_client.select_one(
            table="operators",
            filters={"id": str(operator_id)},
        )

        return self._map_supabase_auth_user_to_operator(
            SupabaseUserResponse(**user.user.model_dump()),
            username=operator_record["username"],
        )

    def get_operators_by_organisation(self, organisation_id: UUID) -> list[Operator]:
        operator_records = self._db_client.select_many(
            table="operators",
            filters={"organisation_id": str(organisation_id)},
        )

        operators = []

        for record in operator_records:
            user = self._auth_client.get_user_by_id(record["id"])

            if user:
                operator = self._map_supabase_auth_user_to_operator(
                    SupabaseUserResponse(**user),
                    username=record["username"],
                )
                operators.append(operator)

        return operators

    def reset_password(
        self,
        organisation_id: UUID,
        operator_id: UUID,
        new_password: str,
    ) -> ResetOperatorPasswordResponse:

        operator_record = self._db_client.select_one(
            table="operators",
            filters={
                "id": str(operator_id),
                "organisation_id": str(organisation_id),
            },
        )

        if not operator_record:
            raise HTTPException(
                status_code=404,
                detail="Operator not found or not part of this organisation.",
            )

        user = self._auth_client.update_user(
            user_id=str(operator_id),
            password=new_password,
        )

        return ResetOperatorPasswordResponse(
            id=user["id"],
            username=operator_record["username"],
            password=new_password,
            organisation_id=organisation_id,
        )