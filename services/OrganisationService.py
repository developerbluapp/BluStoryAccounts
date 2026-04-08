from uuid import UUID
from blustorymicroservices.BluStoryAccounts.repository.OrganisationRepository import OrganisationRepository

class OrganisationService:
    def __init__(self, organisation_repo: OrganisationRepository):
        self._organisation_repo = organisation_repo

    def get_organisation_name_by_id(self, organisation_id: UUID) -> str:
        return self._organisation_repo.get_organisation_name_by_id(organisation_id)
