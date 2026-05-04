import datetime
from dataclasses import dataclass

@dataclass(eq=True)
class BorrowedBook:
    isbn: str
    borrow_date: datetime.date
    expected_return_date: datetime.date
    requested_extension_date: datetime.date | None
