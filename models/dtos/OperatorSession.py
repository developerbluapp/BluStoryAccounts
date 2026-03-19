
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.BluStoryAccounts.models.dtos import Operator
class OperatorSession(BaseModel):
    operator: Operator
    session: Session