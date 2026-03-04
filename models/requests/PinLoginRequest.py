
from uuid import UUID

from pydantic import BaseModel


class PinLoginRequest(BaseModel):
    pin: str