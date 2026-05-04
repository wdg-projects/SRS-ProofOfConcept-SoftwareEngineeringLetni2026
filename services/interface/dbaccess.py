import abc

from .customerdb import CustomerDB

from ...models.book_reservation import BookReservation
from ...models.borrowed_book import BorrowedBook
from ...models.customer import Customer
from ...models.staff import Staff

class PriviliegeError(RuntimeError):
    pass

class DBAccess(abc.ABC):
    """Interface describing a limited-priviliege facade between the database and the outside world."""

    db: CustomerDB

    def __init__(self, db: CustomerDB) -> None:
        self.db = db

    # Logon
    @abc.abstractmethod
    def log_on(self, who: object, password: str) -> str:
        ...

    # Write operations
    @abc.abstractmethod
    def store(self, who: object, token: str, customer: Customer) -> None:
        ...

    @abc.abstractmethod
    def update_staff(self, who: object, token: str, staff: Staff) -> None:
        ...

    # Read operations
    @abc.abstractmethod
    def fetch_reserved_book_by_isbn(self, who: object, token: str, isbn: str) -> BookReservation:
        ...

    @abc.abstractmethod
    def fetch_borrowed_book_by_isbn(self, who: object, token: str, isbn: str) -> BorrowedBook:
        ...

    @abc.abstractmethod
    def fetch_by_library_identifier(self, who: object, token: str, lid: int) -> Customer:
        ...

    @abc.abstractmethod
    def fetch_by_old_library_identifier(self, who: object, token: str, old_lid: str) -> Customer:
        ...

    @abc.abstractmethod
    def fetch_staff_by_employee_id(self, who: object, token: str, eid: int) -> Staff:
        ...

    @abc.abstractmethod
    def set_client_password(self, who: object, token: str, password: str) -> None:
        ...
