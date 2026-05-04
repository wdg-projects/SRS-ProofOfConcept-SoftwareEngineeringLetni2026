import sys, os

here = os.path.realpath(os.path.dirname(__file__))
sys.path.append(here)
os.chdir(here)

from .identity import Identity
# from .accountwizard import AccountCreationInterface
from .viewer import AccountSearcher

# from ..models.customer import Customer

from ..services.localcustomerdb import LocalCustomerDB
from ..services.staffdbaccess import StaffDBAccess

import tkinter as tk

root = tk.Tk()
# AccountCreationInterface(root, access=None, identity=None).pack()
lcdb = LocalCustomerDB("/home/shared/projhere/SEMESTR4/se_proj/test_single.json")
facade = StaffDBAccess(lcdb)
_ = AccountSearcher(root, access=facade, identity=Identity(1, "asdf"))

root.mainloop()
