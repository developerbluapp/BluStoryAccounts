from uuid import UUID

from blustorymicroservices.BluStoryOperators.models.dtos import \
    Organisation, Member
from blustorymicroservices.BluStoryOperators.models.dtos.AuthOrganisation import AuthOrganisation
from blustorymicroservices.BluStoryOperators.models.responses.api.organisations.CreateOrganisationAdminResponse import CreatedOrganisationAdminResponse
from blustorymicroservices.BluStoryOperators.models.responses.api.organisations.OrganisationNameResponse import OrganisationNameResponse
from blustorymicroservices.BluStoryOperators.repository import \
    OrganisationsRepository

from blustorymicroservices.BluStoryOperators.helpers.AuthHelper import AuthHelper
class OrganisationService:
    def __init__(self, organisation_repo: OrganisationsRepository):
        self._organisation_repo = organisation_repo
    def get_organisation_name_by_id(self, organisation_id: UUID) -> str | None:
        return self._organisation_repo.get_organisation_name_by_id(organisation_id)
    def create_and_assign_organisation_admin(self,email:str,organisation_id:UUID) ->  OrganisationNameResponse:
        password = AuthHelper.create_random_password()
        organisation_name = self.get_organisation_name_by_id(organisation_id)
        return self._organisation_repo.create_and_assign_organisation_admin(email,password,organisation_name)
