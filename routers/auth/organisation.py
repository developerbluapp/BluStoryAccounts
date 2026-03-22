# routers/users.py
from typing import Annotated
from uuid import UUID

from blustorymicroservices.BluStoryAccounts.dependencies.services import get_organisation_auth_service
from blustorymicroservices.BluStoryAccounts.models.exceptions.base import \
    AppException
from fastapi import APIRouter, Depends, HTTPException, HTTPException

from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.OrganisationSessionResponse import OrganisationSessionResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.OrganisationResponse import OrganisationResponse
from blustorymicroservices.BluStoryAccounts.models.requests import OrganisationSignupRequest, OrganisationSigninRequest
from blustorymicroservices.BluStoryAccounts.services import OrganisationAuthService
OrganisationAuthServiceDEP = Annotated[OrganisationAuthService, Depends(get_organisation_auth_service)]

router = APIRouter(prefix="/auth/organisation", tags=["auth-organisation"])

@router.post("/signup", response_model=OrganisationSessionResponse ,status_code=201)
def signup_organisation(body: OrganisationSignupRequest, organisation_service: OrganisationAuthServiceDEP):
    session_response= organisation_service.signup_organisation(body)
    return OrganisationSessionResponse(organisation=OrganisationResponse(id=session_response.organisation.id,email=session_response.organisation.email,organisation_id=session_response.organisation.organisation_id,organisation_name=session_response.organisation.organisation_name),session=session_response.session) 

@router.post("/signin", response_model=OrganisationSessionResponse ,status_code=201)
def signin_organisation(body: OrganisationSigninRequest, organisation_service: OrganisationAuthServiceDEP):
    session_response= organisation_service.signin_organisation(body)
    return OrganisationSessionResponse(organisation=OrganisationResponse(id=session_response.organisation.id,email=session_response.organisation.email,organisation_id=session_response.organisation.organisation_id,organisation_name=session_response.organisation.organisation_name),session=session_response.session) 

