# --- Data models ---

from dataclasses import dataclass

@dataclass
class CreatedUser:
    id: str
    email: str
