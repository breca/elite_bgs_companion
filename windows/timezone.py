from pytz import timezone
import datetime as dt
from tkinter import *
from tkinter import ttk

import logging
logger = logging.getLogger(__name__)



class TZWindow(Toplevel):
    """ Create timezone window """

    def __init__(self, parent):
        logging.debug('Opening timezone window.')
        
        # Create TopLevel window
        Toplevel.__init__(self, parent)
        self.transient(parent)
        
        # Set Window geom, frame and layout
        self.geometry("+%d+%d" % (parent.winfo_rootx(), parent.winfo_rooty()))
        self.iconbitmap(parent.conf['theme']['icon'])
        self.title(parent.conf['theme']['titles']['timezone'])

        self.frame = ttk.Frame(self, padding="5 5 5 20")
        self.frame.grid()

        self.timezones = {'Australia, Eastern: ': timezone('Australia/Sydney'),
                          'Australia, Western: ': timezone('Australia/Perth'),
                          'Germany: ': timezone('Europe/Berlin'),
                          'India: ': timezone('Asia/Calcutta'),
                          'Russia, Eastern: ': timezone('Asia/Vladivostok'),
                          'Russia, Western: ': timezone('Europe/Moscow'),
                          'United Kingdom: ': timezone('Europe/London'),
                          'United States, EST: ': timezone('America/New_York'),
                          'United States, PST: ': timezone('America/Los_Angeles')
                          }

        self.top_lbl = Label(self.frame, padx=5, pady=10, text='Loading...')
        self.top_lbl.grid(row=0, column=0, columnspan=2)

        self.after(300, self.refresh)

    def refresh(self):
        self.time = dt.datetime.strftime(dt.datetime.now(), '%H:%M')
        self.top_lbl.configure(text='Times around the world as of {} local time:'.format(self.time))

        self.rows = 1

        for place in self.timezones.keys():
            plc_lbl = Label(self.frame, text=place, justify=RIGHT)
            plc_lbl.grid(row=self.rows, column=0, sticky=E)
            tm = dt.datetime.strftime(dt.datetime.now(self.timezones[place]), '%A, %H:%M')
            tm_lbl = Label(self.frame, text=tm)
            tm_lbl.grid(row=self.rows, column=1)
            self.rows += 1

        self.invis = Label(self.frame, text='   ')
        self.invis.grid(row=self.rows, column=0, columnspan=2, sticky=S)
        self.rows += 1
        self.tz_button = Button(self.frame, padx=20, pady=5, command=self.destroy, text='Ok', anchor=S)
        self.tz_button.grid(row=self.rows, column=0, columnspan=2, sticky=S)
        self.after(1000, self.refresh)