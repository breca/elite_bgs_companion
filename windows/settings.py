from tkinter import *
from tkinter import ttk
import yaml
import logging
logger = logging.getLogger(__name__)


class SettingsWindow(Toplevel):
    """ Create child window: settings """

    def __init__(self, parent, config):
        logger.debug('Creating settings window.')

        # Create TopLevel window
        Toplevel.__init__(self, parent)
        self.transient(parent)

        # Set Window geom, frame and layout
        self.geometry("+%d+%d" % (parent.winfo_rootx(), parent.winfo_rooty()))
        self.iconbitmap(config['theme']['icon'])
        self.title(config['theme']['titles']['settings'])
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid()

        # Initialise variables
        self.option_eddn = BooleanVar()
        self.option_update_check = BooleanVar()
        self.option_ignore_updates = BooleanVar()
        self.option_advisor = BooleanVar()
        self.my_parent = parent

        # Update variables based on settings.yml
        self.option_eddn.set(config['settings']['eddn_enabled'])
        self.option_update_check.set(config['settings']['check_updates_on_start'])
        self.option_ignore_updates.set(config['settings']['ignoring_updates'])
        self.option_advisor.set(config['settings']['show_advisor'])

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
        self.opt_button1 = Button(self.opt_but_frame, padx=20, command=lambda a=config: self.set_options(a),
                                  text='Change settings')
        self.opt_button1.grid(row=0, column=0, sticky=S)
        self.opt_button2 = Button(self.opt_but_frame, padx=20, command=self.die, text='Cancel')
        self.opt_button2.grid(row=0, column=2, sticky=S)

    def set_options(self, config):
        logger.info('Saving options...')
        try:
            config['settings']['eddn_enabled'] = self.option_eddn.get()
            config['settings']['check_updates_on_start'] = self.option_update_check.get()
            config['settings']['ignoring_updates'] = self.option_ignore_updates.get()
            config['settings']['show_advisor'] = self.option_advisor.get()

            with open('settings.yml', 'w') as f:
                yaml.dump(config['settings'], f)
                msg = 'Options saved.'
                logger.info(msg)
                self.my_parent.set_status(msg)
                self.destroy()
                return config

        except Exception as e:
            msg = "Could not update settings.yml!"
            self.my_parent.set_status(msg)
            logger.exception(msg, e)
            self.destroy()
            pass

    def die(self):
        logging.debug('Closing settings window at user request.')
        self.destroy()
