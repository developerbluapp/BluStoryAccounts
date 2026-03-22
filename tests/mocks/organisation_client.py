from uuid import UUID
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.OrganisationNameResponse import OrganisationNameResponse


class MockOrganisationClient:
    def get_organisation_name(self, organisation_id: UUID):
        return OrganisationNameResponse(id=organisation_id, organisation_name="Test Org")