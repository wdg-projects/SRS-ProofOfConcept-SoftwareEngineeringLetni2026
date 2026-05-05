import tkinter as tk
import tkinter.messagebox as tkmsgbox
from typing import Callable

from .viewer import AccountSearcher
from .accountwizard import AccountCreationInterface

from ..services.interface.dbaccess import PriviliegeError
from ..services.interface.remotedb import Remotedb

class LogIn(tk.Toplevel):
    client: Remotedb
    done: Callable[[], object]

    _nfields: int = 0
    _fields: dict[str, tk.StringVar]
    _fin: bool

    emp_id: tk.StringVar
    passwd: tk.StringVar

    def __init__(self, master: tk.Misc | None = None, *, client: Remotedb, done: Callable[[], object]) -> None:
        super().__init__(master)
        self.client = client
        self.done = done

        self._fields = {}
        self._fin = False

        self.emp_id = tk.StringVar()
        self.passwd = tk.StringVar()

        self._add_form_field("Employee Id", self.emp_id)
        self._add_form_field("Password", self.passwd)

        tk.Button(self, text="Log In", command=self.on_submit).grid(row=self._nfields, column=0, columnspan=2)

        self.protocol("WM_DELETE_WINDOW", self.on_delete)

    def _add_form_field(self, name: str, storage: tk.StringVar) -> None:
        tk.Label(self, text=name).grid(row=self._nfields, column=0)
        tk.Entry(self, textvariable=storage).grid(row=self._nfields, column=1)
        self._fields[name] = storage
        self._nfields += 1

    def on_delete(self) -> None:
        if self._fin:
            return
        self.quit()

    def on_submit(self) -> None:
        try:
            eid = int(self.emp_id.get())
        except ValueError:
            _ = tkmsgbox.showerror("Error", "Employee Id must be a number")
            return

        try:
            self.client.log_on_as_staff(eid, self.passwd.get())
        except PriviliegeError as e:
            _ = tkmsgbox.showerror("Login failure", f"{e}")
            return

        self._fin = True
        _ = self.done()
        self.destroy()

class MainPanel(tk.Toplevel):
    client: Remotedb

    def __init__(self, master: tk.Misc | None = None, *, client: Remotedb) -> None:
        super().__init__(master)
        self.client = client

        tk.Label(self, text="What would you like to do?").pack()
        tk.Button(self, text="Create a customer account", command=self.creat).pack()
        tk.Button(self, text="View customer accounts", command=self.view).pack()

        self.protocol("WM_DELETE_WINDOW", self.on_delete)

    def on_delete(self) -> None:
        self.quit()

    def creat(self) -> None:
        _ = AccountCreationInterface(self, client=self.client)

    def view(self) -> None:
        _ = AccountSearcher(self, client=self.client)
