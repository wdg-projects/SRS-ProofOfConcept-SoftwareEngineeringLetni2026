import sys, os

here = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(here)
os.chdir(here)

# from .viewer import AccountSearcher
from .login import LogIn, MainPanel

from ..services.fakeremotedb import FakeRemotedb
from ..services.localcustomerdb import LocalCustomerDB

from ..services.interface.remotedb import Remotedb

import tkinter as tk

def connect() -> Remotedb:
    lcdb = LocalCustomerDB("exampledb.json")
    return FakeRemotedb(lcdb)

root = tk.Tk()
root.withdraw()

client = connect()
def done() -> None:
    _ = MainPanel(root, client=client)
_ = LogIn(root, client=client, done=done)

root.mainloop()
