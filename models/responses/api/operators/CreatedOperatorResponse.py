
from uuid import UUID

from pydantic import BaseModel

from blustorymicroservices.blustory_accounts_auth.models.dtos.Operator import Operator


class CreatedOperatorResponse(BaseModel):
    id: UUID
    username: str
    password: str
    organisation_id: UUID



