import random
import secrets
import string
from pydantic import EmailStr
from uuid import UUID
from blustorymicroservices.blustory_accounts_auth.helpers import OrganisationHelper
from blustorymicroservices.blustory_accounts_auth.models.dtos import \
    AuthMember, MemberSession
from blustorymicroservices.blustory_accounts_auth.models.dtos.MemberDeepLink import MemberDeepLink
from blustorymicroservices.blustory_accounts_auth.providers.interfaces.AuthProvider import AuthProvider

class MemberAuthService:
    def __init__(self,auth_client: AuthProvider):
        self._auth_client = auth_client


    def generate_setup_link(self, email:str) -> str:
        return self._auth_client.generate_magic_link(email, redirect_to=self.settings.deeplink.url)
    

