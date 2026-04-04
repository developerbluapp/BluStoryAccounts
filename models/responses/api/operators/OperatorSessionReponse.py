
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.blustory_accounts_auth.models.responses.api.operators.OperatorResponse import OperatorResponse
class OperatorSessionResponse(BaseModel):
    operator: OperatorResponse
    session: Session