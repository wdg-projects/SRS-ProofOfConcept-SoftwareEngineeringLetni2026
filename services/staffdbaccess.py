from typing import override

from .interface.dbaccess import DBAccess, PriviliegeError

from ..models.book_reservation import BookReservation
from ..models.borrowed_book import BorrowedBook
from ..models.customer import Customer
from ..models.staff import Staff

class StaffDBAccess(DBAccess):

    def _validate(self, who: object, token: str) -> None:
        if not isinstance(who, int):
            raise TypeError("Identity object must be an integer representing the employee ID")
        try:
            staff = self.db.fetch_staff_by_employee_id(who)
        except ValueError:
            raise PriviliegeError("No such employee")
        if staff.session_token != token:
            raise PriviliegeError("Invalid session token")

    @override
    def log_on(self, who: object, password: str) -> str:
        if not isinstance(who, int):
            raise TypeError("Identity object must be an integer representing the employee ID")
        try:
            return self.db.authenticate_staff(who, password)
        except ValueError:
            raise PriviliegeError("Invalid username or password") from None

    @override
    def store(self, who: object, token: str, customer: Customer) -> None:
        self._validate(who, token)
        self.db.store(customer)

    @override
    def update_staff(self, who: object, token: str, staff: Staff) -> None:
        self._validate(who, token)
        self.db.update_staff(staff)

    @override
    def fetch_reserved_book_by_isbn(self, who: object, token: str, isbn: str) -> BookReservation:
        self._validate(who, token)
        return self.db.fetch_reserved_book_by_isbn(isbn)

    @override
    def fetch_borrowed_book_by_isbn(self, who: object, token: str, isbn: str) -> BorrowedBook:
        self._validate(who, token)
        return self.db.fetch_borrowed_book_by_isbn(isbn)

    @override
    def fetch_by_library_identifier(self, who: object, token: str, lid: int) -> Customer:
        self._validate(who, token)
        return self.db.fetch_by_library_identifier(lid)

    @override
    def fetch_by_old_library_identifier(self, who: object, token: str, old_lid: str) -> Customer:
        self._validate(who, token)
        return self.db.fetch_by_old_library_identifier(old_lid)

    @override
    def fetch_staff_by_employee_id(self, who: object, token: str, eid: int) -> Staff:
        self._validate(who, token)
        return self.db.fetch_staff_by_employee_id(eid)

    @override
    def set_client_password(self, who: object, token: str, password: str) -> None:
        raise PriviliegeError("Invalid action; use StaffDBAccess#store to change a client's password")
