from uuid import UUID
from fastapi import HTTPException
from blustorymicroservices.BluStoryAccounts.repository.RoleRepository import RoleRepository
from blustorymicroservices.BluStoryAccounts.repository.UserRoleRepository import UserRoleRepository
from blustorymicroservices.BluStoryAccounts.models.auth import UserRoles

class RolesService:
    def __init__(self, role_repo: RoleRepository, user_role_repo: UserRoleRepository):
        self._role_repo = role_repo
        self._user_role_repo = user_role_repo

    def get_role_id_by_name(self, role_name: str) -> str:
        return self._role_repo.get_role_id(role_name)

    def assign_role_to_user(self, user_id: UUID, role_name: str, organisation_id: str):
        role_id = self.get_role_id_by_name(role_name)
        self._user_role_repo.assign_role(user_id, role_id, organisation_id)

    def get_admin_organisation_id(self, user_id: UUID) -> str:
        role_id = self.get_role_id_by_name(UserRoles.ORGANISATION_ADMIN)
        organisation_id = self._user_role_repo.get_organisation_id_by_user_and_role(user_id, role_id)
        
        if not organisation_id:
            raise HTTPException(status_code=403, detail="OrganisationAdmin admin role not assigned")
        
        return organisation_id
