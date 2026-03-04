import os

from blustorymicroservices.BluStoryLicenseHolders.dependencies.repositories import \
    get_student_repository,get_license_holder_repository
from blustorymicroservices.BluStoryLicenseHolders.repository import \
    LicenseHoldersRepository, StudentsRepository
from blustorymicroservices.BluStoryLicenseHolders.services import LicenseHolderService, StudentService, LicenseHolderAuthService,StudentAuthService

from blustorymicroservices.BluStoryLicenseHolders.settings import (
    EmailSettings, RoleSettings, Settings, SupabaseSettings)
from fastapi import Depends
from supabase import Client


def get_student_service(student_repo: StudentsRepository = Depends(get_student_repository ), license_holder_repo: LicenseHoldersRepository = Depends(get_license_holder_repository)) -> StudentService:
    return StudentService(student_repo, license_holder_repo)

def get_license_holder_service(license_holder_repo: LicenseHoldersRepository = Depends(get_license_holder_repository),student_repo: StudentsRepository = Depends(get_student_repository)) -> LicenseHolderService:
    return LicenseHolderService(license_holder_repo, student_repo)

def get_license_holder_auth_service(
    license_holder_repo: LicenseHoldersRepository = Depends(get_license_holder_repository),
    student_repo: StudentsRepository = Depends(get_student_repository),
) -> LicenseHolderAuthService:
    return LicenseHolderAuthService(license_holder_repo, student_repo)


def get_student_auth_service(student_repo: StudentsRepository = Depends(get_student_repository)) -> StudentAuthService:
    return StudentAuthService(student_repo)