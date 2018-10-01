from tkinter import *
from tkinter import ttk
import logging
logger = logging.getLogger(__name__)

class CrimeWindow(Toplevel):
    def __init__(self, parent):
        # Create TopLevel window
        Toplevel.__init__(self, parent)
        self.transient(parent)

        # Set Window geom, frame and layout
        self.geometry("+%d+%d" % (parent.winfo_rootx(), parent.winfo_rooty()))
        self.iconbitmap(parent.conf['theme']['icon'])
        self.title(parent.conf['theme']['titles']['crime'])

        self.frame = ttk.Frame(self, padding="5 20 5 20")
        self.frame.pack()

        self.templabel = Label(self.frame, text='Coming soon(tm).')
        self.templabel.pack(fill='x', expand=1)

        self.ok_button = Button(self.frame, padx=20, pady=5, command=self.destroy, text='Oooo.', anchor=S)
        self.ok_button.pack(side='bottom')

