# routers/users.py
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryOperators.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends, HTTPException, HTTPException

from blustorymicroservices.BluStoryOperators.models.responses.api.operators.OperatorSessionReponse import OperatorSessionResponse
from blustorymicroservices.BluStoryOperators.models.responses.api.operators.OperatorResponse import OperatorResponse
from dependencies import get_license_holder_auth_service
from models.requests import OperatorSignupRequest, OperatorSigninRequest
from services import OperatorAuthService
OperatorAuthServiceDEP = Annotated[OperatorAuthService, Depends(get_license_holder_auth_service)]

router = APIRouter(prefix="/auth/operator", tags=["auth-operator"])

@router.post("/signup", response_model=OperatorSessionResponse ,status_code=201)
def signup_licenseholder(body: OperatorSignupRequest, licenseholder_service: OperatorAuthServiceDEP):
    session_response= licenseholder_service.signup_license_holder(body)
    return OperatorSessionResponse(operator=OperatorResponse(id=session_response.operator.id,email=session_response.operator.email),session=session_response.session) 

@router.post("/signin", response_model=OperatorSessionResponse ,status_code=201)
def signin_licenseholder(body: OperatorSigninRequest, licenseholder_service: OperatorAuthServiceDEP):
    session_response= licenseholder_service.signin_license_holder(body)
    return OperatorSessionResponse(operator=OperatorResponse(id=session_response.operator.id,email=session_response.operator.email),session=session_response.session) 

