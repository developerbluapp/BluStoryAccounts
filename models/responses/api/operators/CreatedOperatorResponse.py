
from uuid import UUID

from pydantic import BaseModel

from blustorymicroservices.BluStoryOperators.models.dtos.Operator import Operator


class CreatedOperatorResponse(BaseModel):
    id: UUID
    username: str
    password: str
    organisation_id: UUID



