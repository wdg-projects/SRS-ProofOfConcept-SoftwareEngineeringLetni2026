import hashlib
import random
import tkinter as tk
# import tkinter.messagebox as tkmsgbox

from .identity import Identity

from ..models.customer import Customer

from ..services.interface.dbaccess import DBAccess

# FRQ-3.1: The staff user shall be provided a separate interface for customer account creation.

# FRQ-3.2: The customer account creation interface shall provide a way to manually input all user information required for account configuration, as conforming to FRQ-1.2,
#          with the exception of the password hash and modern library card identifier, which shall be left empty.

class AccountCreationInterface(tk.Frame):
    access: DBAccess
    identity: Identity

    _nfields: int = 0
    _fields: dict[str, tk.StringVar]

    first_name: tk.StringVar
    last_name: tk.StringVar
    email: tk.StringVar
    old_library_id: tk.StringVar

    def __init__(self, master: tk.Misc | None = None, *, access: DBAccess, identity: Identity) -> None:
        super().__init__(master)
        self.access = access
        self.identity = identity

        self._fields = {}

        self.first_name = tk.StringVar()
        self.last_name = tk.StringVar()
        self.email = tk.StringVar()
        self.old_library_id = tk.StringVar()

        self._add_form_field("First Name", self.first_name)
        self._add_form_field("Last Name", self.last_name)
        self._add_form_field("E-Mail", self.email)
        self._add_form_field("Old Library ID", self.old_library_id)

        tk.Button(self, text="Create", command=self.on_submit).grid(row=self._nfields, column=0, columnspan=2)

    def _add_form_field(self, name: str, storage: tk.StringVar) -> None:
        tk.Label(self, text=name).grid(row=self._nfields, column=0)
        tk.Entry(self, textvariable=storage).grid(row=self._nfields, column=1)
        self._fields[name] = storage
        self._nfields += 1

    def on_submit(self) -> None:
        fn = self.first_name.get()
        ln = self.last_name.get()
        email = self.email.get()
        old_lid: str | None = self.old_library_id.get()
        if not old_lid:
            old_lid = None

        customer = Customer(fn, ln, email, None, None, None, [], [], old_lid, int.from_bytes(hashlib.md5(f"{fn}{ln}{email}".encode("utf8")).digest()))
        self.access.store(self.identity.employee_id, self.identity.session, customer)

def mock_get_account_creation_interface_form_field(account_creation_interface: AccountCreationInterface, name: str) -> tk.StringVar:
    return account_creation_interface._fields[name]
