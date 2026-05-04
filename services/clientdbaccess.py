from typing import override

from .passwd import hashed_password

from .interface.dbaccess import DBAccess, PriviliegeError

from ..models.book_reservation import BookReservation
from ..models.borrowed_book import BorrowedBook
from ..models.customer import Customer
from ..models.staff import Staff

class ClientDBAccess(DBAccess):

    def _validate(self, who: object, token: str, allow_passwordless: bool) -> int:
        if not isinstance(who, int):
            raise TypeError("Identity object must be an integer representing the customer's library ID")
        try:
            customer = self.db.fetch_by_library_identifier(who)
        except ValueError:
            raise PriviliegeError("No such customer")
        if customer.session_token != token:
            raise PriviliegeError("Invalid session token")
        if (not allow_passwordless) and customer.password_hash is None:
            raise PriviliegeError("Password unset")
        return who

    @override
    def log_on(self, who: object, password: str) -> str:
        if not isinstance(who, int):
            raise TypeError("Identity object must be an integer representing the customer's library ID")
        try:
            return self.db.authenticate_client(who, password)
        except ValueError:
            raise PriviliegeError("Invalid username or password") from None

    @override
    def store(self, who: object, token: str, customer: Customer) -> None:
        lid = self._validate(who, token, False)

        if customer.library_identifier != lid:
            raise PriviliegeError("Can't store other users")
        
        trusted = self.db.fetch_by_library_identifier(lid)

        to_store = Customer(
            trusted.first_name,
            trusted.last_name,
            trusted.email,
            trusted.password_hash,
            trusted.session_token,
            trusted.session_token_expiry,
            trusted.borrowed_books,
            [x for x in trusted.reserved_books if x.accepted] + [x for x in customer.reserved_books if not x.accepted],
            trusted.old_library_id,
            trusted.library_identifier
        )
        if to_store != customer:
            raise PriviliegeError("Unauthorized change to customer state")

        self.db.store(to_store)

    @override
    def update_staff(self, who: object, token: str, staff: Staff) -> None:
        raise PriviliegeError("A client user can't do that")

    @override
    def fetch_reserved_book_by_isbn(self, who: object, token: str, isbn: str) -> BookReservation:
        lid = self._validate(who, token, False)
        customer = self.db.fetch_by_library_identifier(lid)
        for book in customer.reserved_books:
            if book.isbn == isbn:
                return book
        raise PriviliegeError("Not a book reserved by this user")

    @override
    def fetch_borrowed_book_by_isbn(self, who: object, token: str, isbn: str) -> BorrowedBook:
        lid = self._validate(who, token, False)
        customer = self.db.fetch_by_library_identifier(lid)
        for book in customer.borrowed_books:
            if book.isbn == isbn:
                return book
        raise PriviliegeError("Not a book borrowed by this user")

    @override
    def fetch_by_library_identifier(self, who: object, token: str, lid: int) -> Customer:
        this_lid = self._validate(who, token, False)
        if this_lid != lid:
            raise PriviliegeError("Can't fetch other users")
        return self.db.fetch_by_library_identifier(lid)

    @override
    def fetch_by_old_library_identifier(self, who: object, token: str, old_lid: str) -> Customer:
        this_lid = self._validate(who, token, False)
        myself = self.db.fetch_by_library_identifier(this_lid)
        if myself.old_library_id != old_lid:
            raise PriviliegeError("Can't fetch other users")
        return myself

    @override
    def fetch_staff_by_employee_id(self, who: object, token: str, eid: int) -> Staff:
        _ = self._validate(who, token, False)
        raise PriviliegeError("A client user can't do that")

    @override
    def set_client_password(self, who: object, token: str, password: str) -> None:
        lid = self._validate(who, token, True)
        customer = self.db.fetch_by_library_identifier(lid)
        if customer.password_hash is not None:
            raise PriviliegeError("Password already set")
        customer.password_hash = hashed_password(password)
        self.db.store(customer)
