from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: str
    name: str
    email: str
    password: str
    memo: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
