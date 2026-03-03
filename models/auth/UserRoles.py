
from typing import ClassVar

from pydantic import BaseModel


class UserRoles(BaseModel):
    LICENSE_HOLDER: ClassVar[str] = "licenseholder"
    STUDENT: ClassVar[str] = "student"
    PARENT: ClassVar[str] = "parent"
