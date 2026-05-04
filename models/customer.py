import datetime
from dataclasses import dataclass

from .borrowed_book import BorrowedBook
from .book_reservation import BookReservation

@dataclass(eq=True)
class Customer:
    first_name: str
    last_name: str
    email: str
    password_hash: str | None
    session_token: str | None
    session_token_expiry: datetime.datetime | None
    borrowed_books: list[BorrowedBook]
    reserved_books: list[BookReservation]
    old_library_id: str | None
    library_identifier: int | None
