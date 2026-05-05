import tkinter as tk
import tkinter.messagebox as tkmsgbox

from ..models.customer import Customer

from ..services.interface.remotedb import Remotedb

class AccountSearcher(tk.Toplevel):
    client: Remotedb

    mode: tk.StringVar
    idtext: tk.StringVar

    def __init__(self, master: tk.Misc | None = None, *, client: Remotedb) -> None:
        super().__init__(master)
        self.client = client

        self.mode = tk.StringVar()
        self.idtext = tk.StringVar()

        option = tk.OptionMenu(self, self.mode, "Library ID", "Old Library ID")
        option.grid(row=0, column=0)

        entry = tk.Entry(self, textvariable=self.idtext)
        entry.grid(row=0, column=1)

        btn = tk.Button(self, text="Search", command=self.on_submit)
        btn.grid(row=1, column=0, columnspan=2)

    def on_submit(self) -> None:
        idtext = self.idtext.get()
        av = AccountViewer(self, client=self.client)
        if self.mode.get() == "Library ID":
            try:
                lid = int(idtext)
            except ValueError:
                _ = tkmsgbox.showerror("Error", "Modern ID must be numeric")
                return
            av.add_row(self.client.fetch_by_library_identifier(lid))
        else:
            av.add_row(self.client.fetch_by_old_library_identifier(idtext))

class AccountViewer(tk.Toplevel):
    COLS: list[str] = ["Library ID", "First Name", "Last Name", "E-Mail", "Old Library ID"]

    client: Remotedb

    rows: list[list[tuple[tk.Widget, tk.StringVar]]]

    def __init__(self, master: tk.Misc | None = None, *, client: Remotedb) -> None:
        super().__init__(master)
        self.client = client

        self.rows = []

        for i, cols in enumerate(self.COLS):
            tk.Label(self, text=cols).grid(row=0, column=i)
        
        tk.Button(self, text="Submit", command=self.on_submit).grid(row=0, column=len(self.COLS))

    def clear(self) -> None:
        for row in self.rows:
            for elem, _ in row:
                elem.destroy()
        self.rows.clear()

    def add_row(self, customer: Customer) -> None:
        def construct(dft: str, f: bool) -> tuple[tk.Widget, tk.StringVar]:
            var = tk.StringVar(self, dft)
            if f:
                return tk.Entry(self, textvariable=var), var
            return tk.Label(self, textvariable=var), var

        row_data = [customer.library_identifier, customer.first_name, customer.last_name, customer.email, customer.old_library_id]
        editable = [False, True, True, True, True]
        row = [construct("" if dft is None else str(dft), f) for dft, f in zip(row_data, editable)]
        for i, (elem, _) in enumerate(row):
            elem.grid(row=len(self.rows)+1, column=i)
        self.rows.append(row)

    def on_submit(self) -> None:
        for row in self.rows:
            lid, fn, ln, email, old_lid = int(row[0][1].get()), *(x.get() for _, x in row[1:])
            customer = self.client.fetch_by_library_identifier(lid)
            customer.first_name = fn
            customer.last_name = ln
            customer.email = email
            customer.old_library_id = old_lid if old_lid else None
            self.client.store(customer)
        self.destroy()
