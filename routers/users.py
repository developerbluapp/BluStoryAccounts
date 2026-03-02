# routers/users.py
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from services import UserService
from models.requests import CreateUserRequest
from models.responses import CreateUserResponse
from dependencies import get_user_service

UserServiceDep = Annotated[UserService, Depends(get_user_service)]

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/{license_holder_id}", response_model=CreateUserResponse, status_code=201)
def create_user(license_holder_id: UUID, body: CreateUserRequest, service: UserServiceDep):
    try:
        user = service.register_user(body.username, body.password, license_holder_id=str(license_holder_id))
        return CreateUserResponse(id=user.id, email=user.email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{license_holder_id}/students", response_model=list[CreateUserResponse])
def get_students(license_holder_id: UUID, service: UserServiceDep):
    try:
        students = service.get_students_by_license_holder(str(license_holder_id))
        return [CreateUserResponse(id=str(s.id), email=s.email) for s in students]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))