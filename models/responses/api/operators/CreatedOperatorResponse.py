
from uuid import UUID

from pydantic import BaseModel

from blustorymicroservices.BluStoryAccounts.models.dtos.Operator import Operator


class CreatedOperatorResponse(BaseModel):
    id: UUID
    username: str
    password: str
    organisation_id: UUID



