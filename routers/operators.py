# routers/users.py
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryOperators.dependencies.auth import get_current_operator
from blustorymicroservices.BluStoryOperators.models.auth import AuthenticatedOperator
from blustorymicroservices.BluStoryOperators.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends

from blustorymicroservices.BluStoryOperators.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.BluStoryOperators.services import OperatorService
from dependencies import get_operator_service
from services import OperatorService

OperatorDEP = Annotated[OperatorService, Depends(get_operator_service)]
AuthenticatedUserDEP = Annotated[AuthenticatedOperator, Depends(get_current_operator)]
    
router = APIRouter(prefix="/operator", tags=["operator"])

@router.get("/me")                                   # ← protected route
async def get_my_profile(current_user: AuthenticatedUserDEP, operator_service: OperatorDEP):         # ← protected route
    operator = operator_service.get_operator_by_id(current_user.id) # ← ensure license holder exists, otherwise raise 404
    return OperatorResponse(
        id=operator.id,
        email=operator.email)