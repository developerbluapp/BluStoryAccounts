from datetime import datetime

from pydantic import BaseModel


class Organisation(BaseModel):
    id: str
    name:str
    created_at:datetime