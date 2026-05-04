# pyright: reportUninitializedInstanceVariable=false

import sys, os

here = os.path.realpath(os.path.dirname(__file__))
sys.path.append(here)
os.chdir(here)

import unittest
import datetime
import tkinter as tk
from typing import override

from .staffui.identity import Identity
from .staffui.accountwizard import AccountCreationInterface, mock_get_account_creation_interface_form_field

from .services.libraryidgen import LibraryIdSource
from .services.localcustomerdb import LocalCustomerDB
from .services.interface.dbaccess import PriviliegeError
from .services.interface.customerdb import CustomerDB
from .services.staffdbaccess import StaffDBAccess
from .services.clientdbaccess import ClientDBAccess

from .models.staff import Staff
from .models.customer import Customer
from .models.borrowed_book import BorrowedBook
from .models.book_reservation import BookReservation

class MockCustomerDB(CustomerDB):
    data: dict[int, Customer]

    def __init__(self):
        self.data = {}

    @override
    def store(self, customer: Customer) -> None:
        if customer.library_identifier is None:
            raise ValueError("Library identifier must not be None")
        self.data[customer.library_identifier] = customer

    @override
    def fetch_by_library_identifier(self, lid: int) -> Customer:
        return self.data[lid]
    
    @override
    def fetch_by_old_library_identifier(self, old_lid: str) -> Customer:
        raise NotImplementedError

    @override
    def update_staff(self, staff: Staff) -> None:
        raise NotImplementedError

    @override
    def fetch_reserved_book_by_isbn(self, isbn: str) -> BookReservation:
        raise NotImplementedError

    @override
    def fetch_borrowed_book_by_isbn(self, isbn: str) -> BorrowedBook:
        raise NotImplementedError

    @override
    def fetch_staff_by_employee_id(self, eid: int) -> Staff:
        raise NotImplementedError
    
    @override
    def authenticate_staff(self, employee_id: int, password: str) -> str:
        raise NotImplementedError

    @override
    def authenticate_client(self, library_id: int, password: str) -> str:
        raise NotImplementedError

class Tests(unittest.TestCase):
    library_id_source: LibraryIdSource
    mock_customer_db: CustomerDB

    @override
    def setUp(self):
        self.library_id_source = LibraryIdSource()
        self.mock_customer_db = MockCustomerDB()

    def test_customer_data_model(self):    # FRQ-1.2
        bb = BorrowedBook(
            isbn="9780131101630",
            borrow_date=datetime.date(2026, 1, 1),
            expected_return_date=datetime.date(2026, 1, 20),
            requested_extension_date=None
        )

        rv = BookReservation(
            isbn="9780764503894",
            reservation_date=datetime.date(2026, 1, 4),
            accepted=False
        )

        c = Customer(
            first_name="A",
            last_name="B",
            email="a@b.c",
            password_hash=None,
            session_token=None,
            session_token_expiry=None,
            borrowed_books=[bb],
            reserved_books=[rv],
            old_library_id=None,
            library_identifier=None
        )
        lid = c.library_identifier = self.library_id_source.generate(c)

        self.mock_customer_db.store(c)
        self.assertEqual(self.mock_customer_db.fetch_by_library_identifier(lid), c)

class LocalCustomerDBTests(unittest.TestCase):

    def test_empty(self) -> None:  # FRQ-1.1
        lcdb = LocalCustomerDB("test_empty.json")
        with self.assertRaises(ValueError):
            _ = lcdb.fetch_by_library_identifier(1)

    def test_single_read(self) -> None:  # FRQ-1.1
        lcdb = LocalCustomerDB("test_single.json")
        customer = lcdb.fetch_by_library_identifier(1)
        self.assertEqual(customer, Customer(
            "A",
            "B",
            "a@b.c",
            None,
            None,
            None,
            [],
            [],
            None,
            1
        ))

    def test_readback(self) -> None:  # FRQ-1.1
        try:
            os.unlink("test_readback.json")
        except FileNotFoundError:
            pass

        old_customer = Customer(
            "C",
            "B",
            "a@b.c",
            None,
            None,
            None,
            [],
            [BookReservation(
                isbn="9780764503894",
                reservation_date=datetime.date(2026, 1, 4),
                accepted=False
            )],
            None,
            1
        )

        lcdb = LocalCustomerDB("test_readback.json")
        lcdb.store(old_customer)
        del lcdb

        lcdb = LocalCustomerDB("test_readback.json")
        customer = lcdb.fetch_by_library_identifier(1)
        self.assertEqual(customer, old_customer)

    def test_staff_facade(self) -> None:  # FRQ-2.1, FRQ-2.2, FRQ-2.3
        lcdb = LocalCustomerDB("test_single.json")
        facade = StaffDBAccess(lcdb)

        with self.assertRaises(PriviliegeError):
            _ = facade.fetch_by_library_identifier(0, "asdf", 1)

        with self.assertRaises(PriviliegeError):
            _ = facade.fetch_by_library_identifier(1, "gggg", 1)

        _ = facade.fetch_by_library_identifier(1, "asdf", 1)
        facade.update_staff(1, "asdf", facade.fetch_staff_by_employee_id(1, "asdf", 1))

    def test_staff_login(self) -> None:  # FRQ-2.1
        with open("test_single_dup.json", "wb") as fw:
            with open("test_single.json", "rb") as fr:
                _ = fw.write(fr.read())

        lcdb = LocalCustomerDB("test_single_dup.json")
        facade = StaffDBAccess(lcdb)

        with self.assertRaises(PriviliegeError):
            _ = facade.log_on(0, "meow")

        with self.assertRaises(PriviliegeError):
            _ = facade.log_on(1, "asdfasdf")

        session = facade.log_on(1, "meow")
        _ = facade.fetch_by_library_identifier(1, session, 1)

    def test_client_facade(self) -> None:  # FRQ-2.4, FRQ-2.6
        with open("test_double_dup.json", "wb") as fw:
            with open("test_double.json", "rb") as fr:
                _ = fw.write(fr.read())
        lcdb = LocalCustomerDB("test_double_dup.json")
        facade = ClientDBAccess(lcdb)

        with self.assertRaises(PriviliegeError):
            _ = facade.fetch_by_library_identifier(0, "asdf", 1)

        with self.assertRaises(PriviliegeError):
            _ = facade.fetch_by_library_identifier(1, "gggg", 1)

        _ = facade.fetch_by_library_identifier(1, "asdf", 1)

        with self.assertRaises(PriviliegeError):
            _ = facade.fetch_by_library_identifier(1, "asdf", 2)

        with self.assertRaises(PriviliegeError):
            _ = facade.fetch_staff_by_employee_id(1, "asdf", 1)

    def test_client_facade_write(self) -> None:  # FRQ-2.7
        with open("test_double_dup.json", "wb") as fw:
            with open("test_double.json", "rb") as fr:
                _ = fw.write(fr.read())
        lcdb = LocalCustomerDB("test_double_dup.json")
        facade = ClientDBAccess(lcdb)

        this = facade.fetch_by_library_identifier(1, "asdf", 1)

        facade.store(1, "asdf", this)

        this.reserved_books = [BookReservation(isbn="9780764503894", reservation_date=datetime.date(2026, 1, 4), accepted=False)]
        facade.store(1, "asdf", this)

        this.reserved_books = [BookReservation(isbn="9780764503894", reservation_date=datetime.date(2026, 1, 4), accepted=True)]
        with self.assertRaises(PriviliegeError):
            facade.store(1, "asdf", this)

        this.reserved_books = []
        this.first_name = "hehe"
        with self.assertRaises(PriviliegeError):
            facade.store(1, "asdf", this)

    def test_client_login(self) -> None:  # FRQ-2.5, FRQ-2.6
        with open("test_single_dup.json", "wb") as fw:
            with open("test_single.json", "rb") as fr:
                _ = fw.write(fr.read())

        lcdb = LocalCustomerDB("test_single_dup.json")
        facade = ClientDBAccess(lcdb)

        with self.assertRaises(PriviliegeError):
            _ = facade.log_on(0, "meow")

        # Unset password: Accept any
        session = facade.log_on(1, "asdfasdf")

        with self.assertRaises(PriviliegeError):
            _ = facade.fetch_by_library_identifier(1, session, 1)

        facade.set_client_password(1, session, "meow")

        with self.assertRaises(PriviliegeError):
            _ = facade.log_on(1, "asdfasdf")

        session = facade.log_on(1, "meow")
        _ = facade.fetch_by_library_identifier(1, session, 1)

class AccountWizardTests(unittest.TestCase):
    root: tk.Tk

    @override
    def setUp(self) -> None:
        self.root = tk.Tk()

    @override
    def tearDown(self) -> None:
        self.root.destroy()

    def test_account_creation_interface_present(self) -> None:  # FRQ-3.1, FRQ-3.2
        with open("test_single_dup.json", "wb") as fw:
            with open("test_single.json", "rb") as fr:
                _ = fw.write(fr.read())

        cdb = LocalCustomerDB("test_single_dup.json")
        facade = StaffDBAccess(cdb)

        identity = Identity(1, "asdf")

        interface = AccountCreationInterface(self.root, identity=identity, access=facade)

        fields = {
            "First Name": "New",
            "Last Name": "User",
            "E-Mail": "sdfgfdxhb@hfgjn.dfgbfc",
            "Old Library ID": ""
        }

        for field_name, value in fields.items():
            mock_get_account_creation_interface_form_field(interface, field_name).set(value)

    def test_account_creation_interface_present(self) -> None:  # FRQ-3.1, FRQ-3.2, FRQ-3.3
        with open("test_single_dup2.json", "wb") as fw:
            with open("test_single.json", "rb") as fr:
                _ = fw.write(fr.read())

        cdb = LocalCustomerDB("test_single_dup2.json")
        facade = StaffDBAccess(cdb)

        identity = Identity(1, "asdf")

        interface = AccountCreationInterface(self.root, identity=identity, access=facade)

        fields = {
            "First Name": "New",
            "Last Name": "User",
            "E-Mail": "sdfgfdxhb@hfgjn.dfgbfc",
            "Old Library ID": ""
        }

        for field_name, value in fields.items():
            mock_get_account_creation_interface_form_field(interface, field_name).set(value)

        interface.on_submit()
