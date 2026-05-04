# pyright: reportExplicitAny=false, reportAny=false

import codecs
import datetime
import json
import os
from typing import IO, Any, TypedDict, cast, override

from ..models.staff import Staff
from ..models.book_reservation import BookReservation
from ..models.borrowed_book import BorrowedBook
from ..models.customer import Customer

from .passwd import check_password
from .interface.customerdb import CustomerDB

SOURCE = "./db.json"

class StoredStaff(TypedDict):
    employee_id: int
    password_hash: str
    session_token: str | None
    session_token_expiry: int | None

class StoredBorrowedBook(TypedDict):
    isbn: str
    borrow_date: int
    expected_return_date: int
    requested_extension_date: int | None

class StoredBookReservation(TypedDict):
    isbn: str
    reservation_date: int
    accepted: bool

class StoredCustomer(TypedDict):
    first_name: str
    last_name: str
    email: str
    password_hash: str | None
    session_token: str | None
    session_token_expiry: int | None
    borrowed_books: list[str]
    reserved_books: list[str]
    old_library_id: str | None
    library_identifier: int | None

class StoredRoot(TypedDict):
    staff: list[StoredStaff]
    customers: list[StoredCustomer]
    borrowed_books: list[StoredBorrowedBook]
    reserved_books: list[StoredBookReservation]

def staff_from_json(_lcdb: LocalCustomerDB, stored: StoredStaff) -> Staff:
    st_expiry = stored["session_token_expiry"]
    return Staff(
        stored["employee_id"],
        stored["password_hash"],
        stored["session_token"],
        datetime.datetime.fromtimestamp(st_expiry) if st_expiry is not None else None
    )

def borrowed_book_from_json(_lcdb: LocalCustomerDB, stored: StoredBorrowedBook) -> BorrowedBook:
    ext_date = stored["requested_extension_date"]
    return BorrowedBook(
        stored["isbn"],
        datetime.datetime.fromtimestamp(stored["borrow_date"]).date(),
        datetime.datetime.fromtimestamp(stored["expected_return_date"]).date(),
        datetime.datetime.fromtimestamp(ext_date).date() if ext_date is not None else None
    )

def reserved_book_from_json(_lcdb: LocalCustomerDB, stored: StoredBookReservation) -> BookReservation:
    return BookReservation(
        stored["isbn"],
        datetime.datetime.fromtimestamp(stored["reservation_date"]).date(),
        stored["accepted"],
    )

def customer_from_json(lcdb: LocalCustomerDB, stored: StoredCustomer) -> Customer:
    st_expiry = stored["session_token_expiry"]
    return Customer(
        stored["first_name"],
        stored["last_name"],
        stored["email"],
        stored["password_hash"],
        stored["session_token"],
        datetime.datetime.fromtimestamp(st_expiry) if st_expiry is not None else None,
        [lcdb.fetch_borrowed_book_by_isbn(x) for x in stored["borrowed_books"]],
        [lcdb.fetch_reserved_book_by_isbn(x) for x in stored["reserved_books"]],
        stored["old_library_id"],
        stored["library_identifier"],
    )

class LocalCustomerDB(CustomerDB):
    f: IO[str]
    root: StoredRoot
    session_token_expiry: datetime.timedelta

    def __init__(self, source: str = SOURCE, session_token_expiry: datetime.timedelta | None = None) -> None:
        self.session_token_expiry = datetime.timedelta(days=30) if session_token_expiry is None else session_token_expiry

        try:
            self.f = open(source, "r+", encoding="utf8")
        except FileNotFoundError:
            self.f = open(source, "w+", encoding="utf8")
            _ = self.f.write(json.dumps(StoredRoot({
                "staff": [],
                "customers": [],
                "borrowed_books": [],
                "reserved_books": []
            })))
            _ = self.f.seek(0)

        self.root = json.loads(self.f.read())

    def __del__(self) -> None:
        if hasattr(self, "f"):
            self.f.close()

    def flush(self) -> None:
        _ = self.f.truncate(0)
        _ = self.f.seek(0)
        _ = self.f.write(json.dumps(obj=self.root))

    def _store_borrowed(self, src: BorrowedBook) -> str:
        target: dict[str, Any]
        for stored in self.root["borrowed_books"]:
            if stored["isbn"] == src.isbn:
                target = cast(Any, stored)
                break
        else:
            target = {}
            self.root["borrowed_books"].append(cast(Any, target))
        
        target["isbn"] = src.isbn
        target["borrow_date"] = int(datetime.datetime.combine(src.borrow_date, datetime.time(0, 0, 0)).timestamp())
        target["expected_return_date"] = int(datetime.datetime.combine(src.expected_return_date, datetime.time(0, 0, 0)).timestamp())
        target["requested_extension_date"] = None if src.requested_extension_date is None else int(datetime.datetime.combine(src.requested_extension_date, datetime.time(0, 0, 0)).timestamp())

        return src.isbn

    def _store_reserved(self, src: BookReservation) -> str:
        target: dict[str, Any]
        for stored in self.root["reserved_books"]:
            if stored["isbn"] == src.isbn:
                target = cast(Any, stored)
                break
        else:
            target = {}
            self.root["reserved_books"].append(cast(Any, target))
        
        target["isbn"] = src.isbn
        target["reservation_date"] = int(datetime.datetime.combine(src.reservation_date, datetime.time(0, 0, 0)).timestamp())
        target["accepted"] = src.accepted

        return src.isbn

    @override
    def update_staff(self, staff: Staff) -> None:
        target: dict[str, Any]
        for stored in self.root["staff"]:
            if stored["employee_id"] == staff.employee_id:
                target = cast(Any, stored)
                break
        else:
            target = {}
            self.root["staff"].append(cast(Any, target))
        
        target["employee_id"] = staff.employee_id
        target["password_hash"] = staff.password_hash
        target["session_token"] = staff.session_token
        target["session_token_expiry"] = staff.session_token_expiry.timestamp() if staff.session_token_expiry is not None else None

        self.flush()

    @override
    def store(self, customer: Customer) -> None:
        target: dict[str, Any]
        for stored_customer in self.root["customers"]:
            if stored_customer["library_identifier"] == customer.library_identifier:
                target = cast(Any, stored_customer)
                break
        else:
            target = {}
            self.root["customers"].append(cast(Any, target))
        
        target["first_name"] = customer.first_name
        target["last_name"] = customer.last_name
        target["email"] = customer.email
        target["password_hash"] = customer.password_hash
        target["session_token"] = customer.session_token
        target["session_token_expiry"] = None if customer.session_token_expiry is None else int(customer.session_token_expiry.timestamp())
        target["borrowed_books"] = [self._store_borrowed(x) for x in customer.borrowed_books]
        target["reserved_books"] = [self._store_reserved(x) for x in customer.reserved_books]
        target["old_library_id"] = customer.old_library_id
        target["library_identifier"] = customer.library_identifier

        self.flush()

    @override
    def fetch_reserved_book_by_isbn(self, isbn: str) -> BookReservation:
        for book in self.root["reserved_books"]:
            if book["isbn"] == isbn:
                return reserved_book_from_json(self, book)
        raise ValueError(f"Could not find reserved book with ISBN {isbn}")

    @override
    def fetch_borrowed_book_by_isbn(self, isbn: str) -> BorrowedBook:
        for borrowed_book in self.root["borrowed_books"]:
            if borrowed_book["isbn"] == isbn:
                return borrowed_book_from_json(self, borrowed_book)
        raise ValueError(f"Could not find borrowed book with ISBN {isbn}")

    @override
    def fetch_by_library_identifier(self, lid: int) -> Customer:
        for customer in self.root["customers"]:
            if customer["library_identifier"] == lid:
                return customer_from_json(self, customer)
        raise ValueError(f"Could not find customer with library ID {lid}")

    @override
    def fetch_by_old_library_identifier(self, old_lid: str) -> Customer:
        for customer in self.root["customers"]:
            if customer["old_library_id"] == old_lid:
                return customer_from_json(self, customer)
        raise ValueError(f"Could not find customer with old library ID {old_lid}")

    @override
    def fetch_staff_by_employee_id(self, eid: int) -> Staff:
        for staff in self.root["staff"]:
            if staff["employee_id"] == eid:
                return staff_from_json(self, staff)
        raise ValueError(f"Could not find staff with employee ID {eid}")

    @override
    def authenticate_staff(self, employee_id: int, password: str) -> str:
        staff = self.fetch_staff_by_employee_id(employee_id)
        if not check_password(password, staff.password_hash):
            raise ValueError("Wrong password")
        staff.session_token = codecs.encode(os.urandom(32), "hex").decode("ascii")
        staff.session_token_expiry = datetime.datetime.now() + self.session_token_expiry
        self.update_staff(staff)
        return staff.session_token

    @override
    def authenticate_client(self, library_id: int, password: str) -> str:
        client = self.fetch_by_library_identifier(library_id)
        if client.password_hash is not None and not check_password(password, client.password_hash):
            raise ValueError("Wrong password")
        client.session_token = codecs.encode(os.urandom(32), "hex").decode("ascii")
        client.session_token_expiry = datetime.datetime.now() + self.session_token_expiry
        self.store(client)
        return client.session_token
