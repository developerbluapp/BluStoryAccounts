
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.blustory_accounts_auth.models.dtos import Operator
class OperatorSession(BaseModel):
    operator: Operator
    session: Session