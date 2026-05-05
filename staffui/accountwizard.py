import hashlib
import tkinter as tk
# import tkinter.messagebox as tkmsgbox

from ..models.customer import Customer

from ..services.interface.remotedb import Remotedb

# FRQ-3.1: The staff user shall be provided a separate interface for customer account creation.

# FRQ-3.2: The customer account creation interface shall provide a way to manually input all user information required for account configuration, as conforming to FRQ-1.2,
#          with the exception of the password hash and modern library card identifier, which shall be left empty.

class AccountCreationInterface(tk.Toplevel):
    client: Remotedb

    _nfields: int = 0
    _fields: dict[str, tk.StringVar]

    first_name: tk.StringVar
    last_name: tk.StringVar
    email: tk.StringVar
    old_library_id: tk.StringVar

    def __init__(self, master: tk.Misc | None = None, *, client: Remotedb) -> None:
        super().__init__(master)
        self.client = client

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

    def on_submit(self, mock: bool = False) -> None:
        fn = self.first_name.get()
        ln = self.last_name.get()
        email = self.email.get()
        old_lid: str | None = self.old_library_id.get()
        if not old_lid:
            old_lid = None

        lid = int.from_bytes(hashlib.md5(f"{fn}{ln}{email}".encode("utf8")).digest())
        customer = Customer(fn, ln, email, None, None, None, [], [], old_lid, lid)
        self.client.store(customer)

        if not mock:
            popup = tk.Toplevel()
            popup.title("Success")
            tk.Label(popup, text="The library id of the new account is:").grid(row=0,column=0)
            tk.Entry(popup, state="readonly", textvariable=tk.StringVar(popup, str(lid))).grid(row=0,column=1)
        
        self.destroy()

def mock_get_account_creation_interface_form_field(account_creation_interface: AccountCreationInterface, name: str) -> tk.StringVar:
    return account_creation_interface._fields[name]
