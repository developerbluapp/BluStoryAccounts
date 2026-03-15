from uuid import UUID

from blustorymicroservices.BluStoryOperators.models.dtos import \
    Organisation, Member
from blustorymicroservices.BluStoryOperators.repository import \
    OrganisationsRepository


class OrganisationService:
    def __init__(self, organisation_repo: OrganisationsRepository):
        self._organisation_repo = organisation_repo
    def get_organisation_name_by_id(self, organisation_id: UUID) -> str | None:
        return self._organisation_repo.get_organisation_name_by_id(organisation_id)
