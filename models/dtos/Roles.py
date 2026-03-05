
from pydantic import BaseModel

from typing import List



class Roles(BaseModel):
    roles: List[str]
