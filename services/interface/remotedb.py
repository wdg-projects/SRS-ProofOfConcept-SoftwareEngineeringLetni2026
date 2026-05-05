import abc

from ...models.book_reservation import BookReservation
from ...models.borrowed_book import BorrowedBook
from ...models.customer import Customer
from ...models.staff import Staff

class Remotedb(abc.ABC):
    who: object = None
    session: str | None = None

    def set_identity(self, who: object, session: str) -> None:
        self.who = who
        self.session = session

    # Logon
    @abc.abstractmethod
    def log_on_as_staff(self, who: object, password: str) -> None:
        ...

    # Write operations
    @abc.abstractmethod
    def store(self, customer: Customer) -> None:
        ...

    @abc.abstractmethod
    def update_staff(self, staff: Staff) -> None:
        ...

    # Read operations
    @abc.abstractmethod
    def fetch_reserved_book_by_isbn(self, isbn: str) -> BookReservation:
        ...

    @abc.abstractmethod
    def fetch_borrowed_book_by_isbn(self, isbn: str) -> BorrowedBook:
        ...

    @abc.abstractmethod
    def fetch_by_library_identifier(self, lid: int) -> Customer:
        ...

    @abc.abstractmethod
    def fetch_by_old_library_identifier(self, old_lid: str) -> Customer:
        ...

    @abc.abstractmethod
    def fetch_staff_by_employee_id(self, eid: int) -> Staff:
        ...

    @abc.abstractmethod
    def set_client_password(self, password: str) -> None:
        ...
