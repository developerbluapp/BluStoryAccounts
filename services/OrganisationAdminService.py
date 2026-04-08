from uuid import UUID
from blustorymicroservices.BluStoryAccounts.repository.OrganisationRepository import OrganisationRepository
from blustorymicroservices.BluStoryAccounts.repository.OrganisationAdminRepository import OrganisationAdminRepository
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.CreateOrganisationAdminResponse import CreatedOrganisationAdminResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.OrganisationNameResponse import OrganisationNameResponse
from blustorymicroservices.BluStoryAccounts.helpers.AuthHelper import AuthHelper
from blustorymicroservices.BluStoryAccounts.models.auth import UserRoles
from blustorymicroservices.BluStoryAccounts.models.dtos import Roles
from supabase import Client

class OrganisationAdminService:
    def __init__(self, organisation_repo: OrganisationRepository, admin_repo: OrganisationAdminRepository, supabase_client: Client):
        self._organisation_repo = organisation_repo
        self._admin_repo = admin_repo
        self._supabase_client = supabase_client

    def create_and_assign_organisation_admin(self, email: str, organisation_id: UUID) -> CreatedOrganisationAdminResponse:
        # 1. Verify organisation exists
        organisation_name = self._organisation_repo.get_organisation_name_by_id(organisation_id)
        
        # 2. Prepare random password
        password = AuthHelper.create_random_password()
        
        # 3. Get role
        role_id = self._admin_repo.get_role_id(UserRoles.ORGANISATION_ADMIN)
        roles_dto = Roles(roles=[UserRoles.ORGANISATION_ADMIN])

        # 4. Create user in Supabase Auth
        response = self._supabase_client.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"avatar_url": "https://picsum.photos/id/237/200/300"},
            "app_metadata": {"organisation_id": str(organisation_id), "roles": roles_dto.model_dump()["roles"]}
        })

        # 5. Assign role and link to org
        self._admin_repo.assign_role(response.user.id, role_id, str(organisation_id))
        self._admin_repo.link_to_org(response.user.id, str(organisation_id))

        return CreatedOrganisationAdminResponse(
            id=response.user.id,
            email=email,
            password=password,
            organisation_id=organisation_id
        )
