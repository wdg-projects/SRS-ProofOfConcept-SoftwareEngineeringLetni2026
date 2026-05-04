from dataclasses import dataclass

@dataclass(eq=True)
class Identity:
    employee_id: int
    session: str
