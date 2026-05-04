import abc

from ...models.staff import Staff
from ...models.customer import Customer
from ...models.borrowed_book import BorrowedBook
from ...models.book_reservation import BookReservation

class CustomerDB(abc.ABC):

    @abc.abstractmethod
    def store(self, customer: Customer) -> None:
        ...
    
    @abc.abstractmethod
    def update_staff(self, staff: Staff) -> None:
        ...

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
    def authenticate_staff(self, employee_id: int, password: str) -> str:
        ...

    @abc.abstractmethod
    def authenticate_client(self, library_id: int, password: str) -> str:
        ...
