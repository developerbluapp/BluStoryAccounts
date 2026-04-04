# routers/users.py
from typing import Annotated
from uuid import UUID

from blustorymicroservices.blustory_accounts_auth.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends, HTTPException, Header
from blustorymicroservices.blustory_accounts_auth.models.responses.api.operators.CreatedOperatorResponse import CreatedOperatorResponse
from blustorymicroservices.blustory_accounts_auth.models.responses.api.operators.OperatorSessionReponse import OperatorSessionResponse
from blustorymicroservices.blustory_accounts_auth.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.blustory_accounts_auth.dependencies.services import get_operator_auth_service
from blustorymicroservices.blustory_accounts_auth.models.requests import OperatorSigninRequest
from blustorymicroservices.blustory_accounts_auth.services.auth.OperatorAuthService import OperatorAuthService
OperatorAuthServiceDEP = Annotated[OperatorAuthService, Depends(get_operator_auth_service)]

router = APIRouter(tags=["auth-operator"])

@router.post("/auth/operator/signin", response_model=OperatorSessionResponse ,status_code=201)
def signin_operator(body: OperatorSigninRequest, operator_service: OperatorAuthServiceDEP):
    session_response = operator_service.signin_operator(body)
    return OperatorSessionResponse(operator=OperatorResponse(id=session_response.operator.id,username=session_response.operator.username),session=session_response.session) 

# This was previously in /admin/operator
@router.post("/admin/operator", response_model=CreatedOperatorResponse, status_code=201)
def signup_operator(operator_service: OperatorAuthServiceDEP, authorization: Annotated[str, Header()]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    
    return operator_service.signup_operator(token)
