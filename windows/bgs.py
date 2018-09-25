from tkinter import *
from tkinter import ttk
from lib.debased import Debaser
from string import Template
import logging
logger = logging.getLogger(__name__)


class BgsWindow(Toplevel):
    """
    Create child window: bgs report
    Initial window is more or less blank until results are fetched.
    """

    def __init__(self, parent, config):
        logger.debug('Creating BGS report.')

        # Create TopLevel window
        Toplevel.__init__(self, parent)
        self.transient(parent)

        # Set Window geom, frame and layout
        self.geometry("+%d+%d" % (parent.winfo_rootx(), parent.winfo_rooty()))
        self.iconbitmap(config['theme']['icon'])
        self.title(config['theme']['titles']['bgs'])

        # Initialise variables
        self.my_parent = parent   # Used to set strings in the main window
        self.my_strings = config['string']['window']['bgs']
        self.bgs = {}
        self.old_bgs = {}
        self.result_frame = ""   # Used to display transaction data on Canvas

        # Initial window elements
        # Create a canvas, then a frame embedded into the canvas. Attach a scrollbar to the canvas
        # qv https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter
        self.canvas = Canvas(self, width=730, height=200)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas_frame = ttk.Frame(self.canvas, padding="10 10 10 10")
        self.canvas_frame.bind("<Configure>", lambda event, canvas=self.canvas: self.on_frame_configure())
        self.canvas_frame.pack()

        # Capture the window id for later destruction
        self.prefetch_window = self.canvas.create_window((4, 4), window=self.canvas_frame, anchor="nw")

        if not hasattr(self, 'prefetch_textfield'):
            print('STUB')
            self.prefetch_textfield = StringVar()
            self.prefetch_textfield.set('Loading, please wait.')

        self.prefetch_label = Label(self.canvas_frame, textvariable=self.prefetch_textfield)
        self.prefetch_label.pack(anchor=N)

        self.db = Debaser()
        self.poll_database()

    def poll_database(self):
        """ Poll the database for fresh transaction data """
        transactions = self.db.get('transactions')
        if len(transactions) == 0:
            logging.debug('Reporting no transactions found')
            self.prefetch_textfield.set(self.my_strings['no_results'])
        else:
            self.bgs = transactions
        self.after(1000, self.poll_database)

    def on_frame_configure(self):
        """ Reset the scroll region to encompass the inner frame """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def die(self):
        logging.debug('Closing BGS window at user request.')
        self.destroy()

    def draw_results(self):
        """ Redraw the BGS window grid if there's any changes in transaction data """

        if self.old_bgs != self.bgs:
            self.old_bgs = self.bgs

        self.prefetch_label.destroy()  # Remove prefetch text

        self.result_frame = ttk.Frame(self.canvas_frame)  # Create new grid on Canvas
        self.result_frame.grid()

        self.bgs_title_system = Label(self.canvas_frame)
        self.bgs_title_system = Label(self.canvas_frame)
        self.bgs_title_category_bounty = Label(self.canvas_frame)
        self.bgs_title_category_combat = Label(self.canvas_frame)
        self.bgs_title_category_donation = Label(self.canvas_frame)
        self.bgs_title_category_trade = Label(self.canvas_frame)
        self.bgs_title_category_mission = Label(self.canvas_frame)
        self.bgs_title_category_exploration = Label(self.canvas_frame)
        self.bgs_title_category_crime = Label(self.canvas_frame)

        rows = 0
        bgs_text = Template(config['bgs']['bgs_string'])

        for system in self.bgs:
            for station in self.bgs[system]:
                for faction in self.bgs[system][station]:
                    logging.debug('Processing faction: ' + faction)

                    # Counts for mission influence
                    count_mission_inf_none = 0
                    count_mission_inf_low = 0
                    count_mission_inf_med = 0
                    count_mission_inf_high = 0

                    # Counts for number of transactions carried out
                    count_bounty = 0
                    count_combat = 0
                    count_donation = 0
                    count_trade_loss = 0    # trades at a loss (offensive BGS)
                    count_trade_low = 0     # trades under 700 credit profit
                    count_trade_high = 0    # trades above 700 credit profit
                    count_smuggling_low = 0  # As above but for sneaky trades
                    count_smuggling_high = 0
                    count_mission = 0         # Number of completed missions
                    count_mission_dumped = 0  # Number of accepted and then dropped missions
                    count_exploration = 0
                    count_crimes = 0        # Murders / Assaults carried out

                    self.fact_lbl = Label(self.canvas_frame, text=faction, padx=3, pady=3, borderwidth=1, relief='ridge', anchor=W, font = "Verdana 10 bold")
                    self.fact_lbl.grid(row=rows, column=0, columnspan=9, padx=3, pady=3, sticky=E+W)
                    rows+=1
                    title_lbl_1 = Label(self.canvas_frame, text='System', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_1.grid(row=rows, column=0, sticky=NSEW)
                    title_lbl_2 = Label(self.canvas_frame, text='Station', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_2.grid(row=rows, column=1, sticky=NSEW)
                    title_lbl_2 = Label(self.canvas_frame, text='Bounties', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_2.grid(row=rows, column=2, sticky=NSEW)
                    title_lbl_3 = Label(self.canvas_frame, text='Combat\nBonds', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_3.grid(row=rows, column=3, sticky=NSEW)
                    title_lbl_4 = Label(self.canvas_frame, text='Crime', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_4.grid(row=rows, column=8, sticky=NSEW)
                    title_lbl_5 = Label(self.canvas_frame, text='Donations', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_5.grid(row=rows, column=4, sticky=NSEW)
                    title_lbl_6 = Label(self.canvas_frame, text='Exploration', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_6.grid(row=rows, column=8, sticky=NSEW)
                    title_lbl_7 = Label(self.canvas_frame, text='Missions', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_7.grid(row=rows, column=5, sticky=NSEW)
                    title_lbl_8 = Label(self.canvas_frame, text='Trade', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_8.grid(row=rows, column=6, sticky=NSEW)
                    title_lbl_9 = Label(self.canvas_frame, text='Smuggling', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_9.grid(row=rows, column=7, sticky=NSEW)

                    rows += 1
                    ##bgs_string: $value > $type > $faction > $station > $system
                    if 'bounty' in self.bgs[system][station][faction]['transactions'].keys():
                        button_string = bgs_text.safe_substitute(
                            value = self.bgs[system][station][faction]['transactions']['amount'],
                            type = "Bounties"
                        )

                    # FINISH ME


