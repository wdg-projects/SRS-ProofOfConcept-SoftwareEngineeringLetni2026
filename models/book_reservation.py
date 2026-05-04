import datetime
from dataclasses import dataclass

@dataclass(eq=True)
class BookReservation:
    isbn: str
    reservation_date: datetime.date
    accepted: bool
