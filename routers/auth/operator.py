# routers/users.py
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryAccounts.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends, HTTPException, HTTPException

from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.OperatorSessionReponse import OperatorSessionResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.BluStoryAccounts.dependencies import get_operator_auth_service
from blustorymicroservices.BluStoryAccounts.models.requests import OperatorSignupRequest, OperatorSigninRequest
from blustorymicroservices.BluStoryAccounts.services import OperatorAuthService
OperatorAuthServiceDEP = Annotated[OperatorAuthService, Depends(get_operator_auth_service)]

router = APIRouter(prefix="/auth/operator", tags=["auth-operator"])

@router.post("/signin", response_model=OperatorSessionResponse ,status_code=201)
def signin_operator(body: OperatorSigninRequest, operator_service: OperatorAuthServiceDEP):
    session_response= operator_service.signin_operator(body)
    return OperatorSessionResponse(operator=OperatorResponse(id=session_response.operator.id,username=session_response.operator.username),session=session_response.session) 
