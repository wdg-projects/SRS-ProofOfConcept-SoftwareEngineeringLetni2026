import datetime
from dataclasses import dataclass

@dataclass(eq=True)
class Staff:
    employee_id: int
    password_hash: str
    session_token: str | None
    session_token_expiry: datetime.datetime | None
