
from typing import ClassVar

from pydantic import BaseModel


class UserRoles(BaseModel):
    LICENSE_HOLDER: ClassVar[str] = "operator"
    STUDENT: ClassVar[str] = "member"
    PARENT: ClassVar[str] = "parent"
    ORGANISATION_ADMIN: ClassVar[str] = "organisation_admin"