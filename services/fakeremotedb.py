from typing import override

from .staffdbaccess import StaffDBAccess

from .interface.dbaccess import DBAccess, PriviliegeError
from .interface.remotedb import Remotedb
from .interface.customerdb import CustomerDB

from ..models.book_reservation import BookReservation
from ..models.borrowed_book import BorrowedBook
from ..models.customer import Customer
from ..models.staff import Staff

class FakeRemotedb(Remotedb):
    cdb: CustomerDB
    facade: DBAccess | None = None

    def __init__(self, cdb: CustomerDB) -> None:
        self.cdb = cdb

    def _verify_logged_in(self) -> tuple[DBAccess, str]:
        if self.facade is None or self.session is None:
            raise PriviliegeError("Not logged in")
        return self.facade, self.session

    # Logon
    @override
    def log_on_as_staff(self, who: object, password: str) -> None:
        if self.session is not None:
            raise PriviliegeError("Already logged in")
        self.facade = StaffDBAccess(self.cdb)
        self.set_identity(who, self.facade.log_on(who, password))

    # Write operations
    @override
    def store(self, customer: Customer) -> None:
        fc, sess = self._verify_logged_in()
        fc.store(self.who, sess, customer)

    @override
    def update_staff(self, staff: Staff) -> None:
        fc, sess = self._verify_logged_in()
        fc.update_staff(self.who, sess, staff)

    # Read operations
    @override
    def fetch_reserved_book_by_isbn(self, isbn: str) -> BookReservation:
        fc, sess = self._verify_logged_in()
        return fc.fetch_reserved_book_by_isbn(self.who, sess, isbn)

    @override
    def fetch_borrowed_book_by_isbn(self, isbn: str) -> BorrowedBook:
        fc, sess = self._verify_logged_in()
        return fc.fetch_borrowed_book_by_isbn(self.who, sess, isbn)

    @override
    def fetch_by_library_identifier(self, lid: int) -> Customer:
        fc, sess = self._verify_logged_in()
        return fc.fetch_by_library_identifier(self.who, sess, lid)

    @override
    def fetch_by_old_library_identifier(self, old_lid: str) -> Customer:
        fc, sess = self._verify_logged_in()
        return fc.fetch_by_old_library_identifier(self.who, sess, old_lid)

    @override
    def fetch_staff_by_employee_id(self, eid: int) -> Staff:
        fc, sess = self._verify_logged_in()
        return fc.fetch_staff_by_employee_id(self.who, sess, eid)

    @override
    def set_client_password(self, password: str) -> None:
        fc, sess = self._verify_logged_in()
        return fc.set_client_password(self.who, sess, password)
