from tkinter import *
from tkinter import ttk
import yaml
import logging
logger = logging.getLogger(__name__)


class SettingsWindow(Toplevel):
    """ Create child window: settings """

    def __init__(self, parent):
        logger.debug('Creating settings window.')

        # Create TopLevel window
        Toplevel.__init__(self, parent)
        self.transient(parent)

        # Set Window geom, frame and layout
        self.geometry("+%d+%d" % (parent.winfo_rootx(), parent.winfo_rooty()))
        self.iconbitmap(parent.conf['theme']['icon'])
        self.title(parent.conf['theme']['titles']['settings'])
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid()

        # Initialise variables
        self.set_status = parent.set_status   # Used to set strings in the main window
        self.option_eddn = BooleanVar()
        self.option_update_check = BooleanVar()
        self.option_ignore_updates = BooleanVar()
        self.option_advisor = BooleanVar()
        self.conf = parent.conf

        # Update variables based on settings.yml
        self.option_eddn.set(self.conf['settings']['eddn_enabled'])
        self.option_update_check.set(self.conf['settings']['check_updates_on_start'])
        self.option_ignore_updates.set(self.conf['settings']['ignoring_updates'])
        self.option_advisor.set(self.conf['settings']['show_advisor'])

        # Window elements
        self.opt1 = Label(self.frame, text='Automatically check for updates on startup',
                          padx=0, pady=0, anchor=W, justify=LEFT)
        self.opt1.grid(row=1, column=1, sticky=W)
        self.chk1 = Checkbutton(self.frame, variable=self.option_update_check)
        self.chk1.grid(row=1, column=0)

        self.opt2 = Label(self.frame, text='Ignore Updates',
                          padx=0, pady=0, anchor=W, justify=LEFT)
        self.opt2.grid(row=2, column=1, sticky=W)
        self.chk2 = Checkbutton(self.frame, variable=self.option_ignore_updates)
        self.chk2.grid(row=2, column=0)

        self.opt3 = Label(self.frame, text='Show Advisor (requires restart)', padx=0, pady=0, anchor=W, justify=LEFT)
        self.opt3.grid(row=3, column=1, sticky=W)
        self.chk3 = Checkbutton(self.frame, variable=self.option_advisor)
        self.chk3.grid(row=3, column=0)

        self.opt4 = Label(self.frame, text='Anonymously upload system/station/market'
                          'data to the Elite Dangerous Data Network', padx=0,
                           pady=0, anchor=W, justify=LEFT)
        self.opt4.grid(row=4, column=1, sticky=W)
        self.chk4 = Checkbutton(self.frame, variable=self.option_eddn)
        self.chk4.grid(row=4, column=0)

        # Additional frame for buttons
        self.opt_but_frame = ttk.Frame(self, padding="10 10 10 10")
        self.opt_but_frame.grid()

        # Add buttons to button frame
        self.opt_button1 = Button(self.opt_but_frame, padx=20, command=lambda: self.set_options(),
                                  text='Change settings')
        self.opt_button1.grid(row=0, column=0, sticky=S)
        self.opt_button2 = Button(self.opt_but_frame, padx=20, command=self.die, text='Cancel')
        self.opt_button2.grid(row=0, column=2, sticky=S)

    def set_options(self):
        logger.info('Saving options...')
        try:
            self.conf['settings']['eddn_enabled'] = self.option_eddn.get()
            self.conf['settings']['check_updates_on_start'] = self.option_update_check.get()
            self.conf['settings']['ignoring_updates'] = self.option_ignore_updates.get()
            self.conf['settings']['show_advisor'] = self.option_advisor.get()

            with open('settings.yml', 'w') as f:
                yaml.dump(self.conf['settings'], f)
                self.set_status('Options saved.')
                logger.info('Options saved.')
                logger.debug('Options: {}'.format(str(self.conf['settings'])))
                self.destroy()

        except Exception as e:
            self.set_status("Could not update settings.yml!")
            logger.exception("Could not update settings.yml!", e)
            self.destroy()
            pass

    def die(self):
        logging.debug('Closing settings window at user request.')
        self.destroy()
