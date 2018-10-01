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

    def __init__(self, parent):
        logger.debug('Creating BGS report.')

        # Create TopLevel window
        Toplevel.__init__(self, parent)
        self.transient(parent)

        # Set Window geom, frame and layout
        self.geometry("+%d+%d" % (parent.winfo_rootx(), parent.winfo_rooty()))
        self.iconbitmap(parent.conf['theme']['icon'])
        self.title(parent.conf['theme']['titles']['bgs'])

        # Initialise variables
        self.set_status = parent.set_status   # Used to set strings in the main window
        self.strings = parent.conf['string']['window']['bgs']
        self.bgsconf = parent.conf['bgs']
        self.bgs = {}
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
        self.refresh()

    def refresh(self):
        """ Poll the database and redraw the window """
        logging.debug('Refreshing BGS report')
        self.poll_database()
        if len(self.bgs) > 0:
            self.draw_results()
        self.after(1000, self.refresh)


    def poll_database(self):
        """ Poll the database for fresh transaction data """
        transactions = self.db.get('transactions')
        num_transactions = len(transactions)
        if num_transactions == 0:
            logging.debug('Reporting no transactions found')
            self.prefetch_textfield.set(self.strings['no_results'])
        else:
            logging.debug('{} transactions found'.format(num_transactions))
            self.bgs = transactions

    def on_frame_configure(self):
        """ Reset the scroll region to encompass the inner frame """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def die(self):
        logging.debug('Closing BGS window at user request.')
        self.destroy()

    def draw_results(self):
        """ Redraw the BGS window grid if there's any changes in transaction data """

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

        for system in self.bgs:
            for station in self.bgs[system]:
                for faction in self.bgs[system][station]:
                    logging.debug('Processing faction: {} in system {}').format(faction, system)

                    # # Counts for mission influence
                    # count_mission_inf_none = 0
                    # count_mission_inf_low = 0
                    # count_mission_inf_med = 0
                    # count_mission_inf_high = 0
                    #
                    # # Counts for number of transactions carried out
                    # count_bounty = 0
                    # count_combat = 0
                    # count_donation = 0
                    # count_trade_loss = 0    # trades at a loss (offensive BGS)
                    # count_trade_low = 0     # trades under 700 credit profit
                    # count_trade_high = 0    # trades above 700 credit profit
                    # count_smuggling_low = 0  # As above but for sneaky trades
                    # count_smuggling_high = 0
                    # count_mission = 0         # Number of completed missions
                    # count_mission_dumped = 0  # Number of accepted and then dropped missions
                    # count_exploration = 0
                    # count_crimes = 0        # Murders / Assaults carried out

                    fact_lbl = Label(self.canvas_frame, text=faction, padx=3, pady=3, borderwidth=1,
                                          relief='ridge', anchor=W, font="Verdana 10 bold")
                    fact_lbl.grid(row=rows, column=0, columnspan=9, padx=3, pady=3, sticky=E+W)
                    rows+=1
                    title_lbl_1 = Label(self.canvas_frame, text='System', borderwidth=1, relief='raised', padx=3,
                                        pady=3)
                    title_lbl_1.grid(row=rows, column=0, sticky=NSEW)
                    title_lbl_2 = Label(self.canvas_frame, text='Station', borderwidth=1, relief='raised', padx=3,
                                        pady=3)
                    title_lbl_2.grid(row=rows, column=1, sticky=NSEW)

                    title_lbl_2 = Label(self.canvas_frame, text='Bounties', borderwidth=1, relief='raised', padx=3,
                                        pady=3)
                    title_lbl_2.grid(row=rows, column=2, sticky=NSEW)
                    title_lbl_3 = Label(self.canvas_frame, text='Combat\nBonds', borderwidth=1, relief='raised', padx=3,
                                        pady=3)
                    title_lbl_3.grid(row=rows, column=3, sticky=NSEW)
                    title_lbl_4 = Label(self.canvas_frame, text='Exploration', borderwidth=1, relief='raised', padx=3,
                                        pady=3)
                    title_lbl_4.grid(row=rows, column=8, sticky=NSEW)
                    title_lbl_5 = Label(self.canvas_frame, text='Missions', borderwidth=1, relief='raised', padx=3,
                                        pady=3)
                    title_lbl_5.grid(row=rows, column=5, sticky=NSEW)
                    title_lbl_6 = Label(self.canvas_frame, text='Smuggling', borderwidth=1, relief='raised', padx=3,
                                        pady=3)
                    title_lbl_6.grid(row=rows, column=7, sticky=NSEW)
                    title_lbl_7 = Label(self.canvas_frame, text='Trade', borderwidth=1, relief='raised', padx=3,
                                        pady=3)
                    title_lbl_7.grid(row=rows, column=6, sticky=NSEW)

                    rows += 1

                    syst = Label(self.canvas_frame, text=system, padx=3, pady=3)
                    syst.grid(row=rows, column=0, padx=3, pady=3)
                    stat = Label(self.canvas_frame, text=station, padx=3, pady=3)
                    stat.grid(row=rows, column=1, padx=3, pady=3)

                    # If transaction present, compile string template and substitute string markers with data
                    # Bounty transactions
                    if 'bounty' in self.bgs[system][station][faction]['transactions'].keys():
                        transaction = self.bgs[system][station][faction]['transactions']['bounty']
                        button_template = self.bgsconf['types']['bounty']['start_field'] + \
                            self.bgsconf['types']['bounty']['kills'] + \
                            self.bgsconf['types']['bounty']['transaction_count']

                        if transaction['commanders'] > 0:
                            button_template += self.bgsconf['types']['bounty']['cmdr_report_start']

                            cmdr_substring = Template(self.bgsconf['types']['bounty']['cmdr_report_entry'])
                            for cmdr in transaction['cmdr_names'].keys():
                                button_template += cmdr_substring.safe_substitute(cmdr_name=cmdr.key(),
                                                                         cmdr_individualcount=cmdr.value())

                            button_template += self.bgsconf['types']['combat_bonds']['cmdr_report_end']

                        button_template += self.bgsconf['types']['combat_bonds']['end_field']

                        amount_nice = '{:,}'.format(transaction['amount'])
                        button_template = Template(button_template)
                        btn_string = button_template.safe_substitute(
                            amount=amount_nice,
                            kills=transaction['kills'],
                            transaction_count=transaction['count'],
                            cmdr_killcount=transaction['commanders']
                        )

                        lbl1 = Button(self.canvas_frame, text=amount_nice, borderwidth=1, relief='sunken',
                                      padx=10, pady=3, command=lambda j=btn_string: self.copy_to_clipboard(self, j))
                        lbl1.grid(row=rows, column=2, padx=3, pady=3, sticky=NSEW)

                    # Combat bond transactions
                    if 'combat' in self.bgs[system][station][faction]['transactions'].keys():
                        transaction = self.bgs[system][station][faction]['transactions']['combat']
                        button_template = self.bgsconf['types']['combat']['start_field'] + \
                            self.bgsconf['types']['combat']['kills'] + \
                            self.bgsconf['types']['combat']['transaction_count']

                        if transaction['commanders'] > 0:
                            button_template += self.bgsconf['types']['combat']['cmdr_report_start']

                            cmdr_substring = Template(self.bgsconf['types']['combat']['cmdr_report_entry'])
                            for cmdr in transaction['cmdr_names'].keys():
                                button_template += cmdr_substring.safe_substitute(cmdr_name=cmdr.key(),
                                                                         cmdr_individualcount=cmdr.value())

                            button_template += self.bgsconf['types']['combat_bonds']['cmdr_report_end']

                        button_template += self.bgsconf['types']['combat_bonds']['end_field']

                        amount_nice = '{:,}'.format(transaction['amount'])
                        button_template = Template(button_template)
                        btn_string = button_template.safe_substitute(
                            amount=amount_nice,
                            kills=transaction['kills'],
                            transaction_count=transaction['count'],
                            cmdr_killcount=transaction['commanders']
                        )

                        lbl2 = Button(self.canvas_frame, text=amount_nice, borderwidth=1, relief='sunken',
                                      padx=10, pady=3, command=lambda j=btn_string: self.copy_to_clipboard(self, j))
                        lbl2.grid(row=rows, column=2, padx=3, pady=3, sticky=NSEW)

                    # Exploration transactions
                    if 'exploration' in self.bgs[system][station][faction]['transactions'].keys():
                        transaction = self.bgs[system][station][faction]['transactions']['exploration']

                        button_template = self.bgsconf['types']['exploration']['start_field'] + \
                                          self.bgsconf['types']['exploration']['transaction_count'] + \
                                          self.bgsconf['types']['exploration']['end_field']

                        amount_nice = '{:,}'.format(transaction['amount'])
                        button_template = Template(button_template)
                        btn_string = button_template.safe_substitute(
                            amount=amount_nice,
                            transaction_count = transaction['count']
                        )

                        lbl3 = Button(self.canvas_frame, text=amount_nice, borderwidth=1, relief='sunken',
                                      padx=10, pady=3, command=lambda j=btn_string: self.copy_to_clipboard(self, j))
                        lbl3.grid(row=rows, column=2, padx=3, pady=3, sticky=NSEW)

                    # Mission transactions
                    if 'mission' in self.bgs[system][station][faction]['transactions'].keys():
                        if len(self.bgs[system][station][faction]['transactions']['mission']['id']) > 0:
                            mission_influence = self.bgs[system][station][faction]['transactions']['mission']['completed']
                            abandoned = self.bgs[system][station][faction]['transactions']['mission']['abandoned']
                            amount = self.bgs[system][station][faction]['transactions']['mission']['amount']

                            button_template = self.bgsconf['types']['mission']['start_field']

                            for x in ['high', 'med', 'low']:
                                if x in mission_influence.keys():
                                    substr = Template(self.bgsconf['types']['mission']['completed'][x]).safe_substitute(
                                        mission_influence[x]
                                    )
                                    button_template += substr

                            if abandoned:
                                substr = Template(self.bgsconf['types']['mission']['abandoned']).safe_substitute(
                                    abandoned)
                                button_template += substr

                            button_template += self.bgsconf['types']['mission']['end_field']

                            amount_nice = '{:,}'.format(amount)
                            button_template = Template(button_template)
                            btn_string = button_template.safe_substitute(amount=amount_nice)

                            lbl4 = Button(self.canvas_frame, text=amount_nice, borderwidth=1, relief='sunken',
                                          padx=10, pady=3,
                                          command=lambda j=btn_string: self.copy_to_clipboard(self, j))
                            lbl4.grid(row=rows, column=2, padx=3, pady=3, sticky=NSEW)

                    # Smuggling transactions
                    if 'smuggled' in self.bgs[system][station][faction]['transactions'].keys():
                        trades = self.bgs[system][station][faction]['transactions']['smuggled']['count']
                        amount = self.bgs[system][station][faction]['transactions']['smuggled']['amount']

                        button_template = self.bgsconf['types']['smuggling']['start_field']

                        for x in ['high', 'normal', 'loss']:
                            if x in trades.keys():
                                substrvals = {
                                    x: trades[x],
                                    'commodity_types': trades[x + '_commtypes']
                                }
                                substr = Template(self.bgsconf['types']['smuggling'][x]).safe_substitute(substrvals)
                                button_template += substr

                        amount_nice = '{:,}'.format(amount)
                        button_template = Template(button_template)
                        btn_string = button_template.safe_substitute(amount=amount_nice)

                        lbl5 = Button(self.canvas_frame, text=amount_nice, borderwidth=1, relief='sunken',
                                      padx=10, pady=3,
                                      command=lambda j=btn_string: self.copy_to_clipboard(self, j))
                        lbl5.grid(row=rows, column=2, padx=3, pady=3, sticky=NSEW)

                    # Trade transactions
                    if 'trade' in self.bgs[system][station][faction]['transactions'].keys():
                        trades = self.bgs[system][station][faction]['transactions']['trade']['count']
                        amount = self.bgs[system][station][faction]['transactions']['trade']['amount']

                        button_template = self.bgsconf['types']['trade']['start_field']

                        for x in ['high', 'normal', 'loss']:
                            if x in trades.keys():
                                substrvals = {
                                    x: trades[x],
                                    'commodity_types': trades[x + '_commtypes']
                                }
                                substr = Template(self.bgsconf['types']['smuggling'][x]).safe_substitute(substrvals)
                                button_template += substr

                        amount_nice = '{:,}'.format(amount)
                        button_template = Template(button_template)
                        btn_string = button_template.safe_substitute(amount=amount_nice)

                        lbl6 = Button(self.canvas_frame, text=amount_nice, borderwidth=1, relief='sunken',
                                      padx=10, pady=3,
                                      command=lambda j=btn_string: self.copy_to_clipboard(self, j))
                        lbl6.grid(row=rows, column=2, padx=3, pady=3, sticky=NSEW)

                    rows += 1


                    # if 'crime' in self.bgs[system].keys():
                    #     for transaction in self.bgs[system][station][faction]['transactions']['combat']:
                    #         button_template = self.bgsconf['types']['combat_bonds']['start_field'] + \
                    #         self.bgsconf['types']['combat_bonds']['kills'] + \
                    #         self.bgsconf['types']['combat_bonds']['transaction_count']
                    #
                    #         if transaction['commanders'] > 0:
                    #             button_template += self.bgsconf['types']['combat_bonds']['cmdr_report']
                    #         button_template += self.bgsconf['types']['combat_bonds']['end_field']
                    #
                    #         button_template = Template(button_template)
                    #         btn_string = button_template.safe_substitute(
                    #             amount=transaction['amount'],
                    #             kills=transaction['kills'],
                    #             transaction_count = transaction['count'],
                    #             cmdr_count=transaction['commanders'],
                    #             cmdr_names=transaction['cmdr_names']
                    #         )
                    #
                    #         amount_nice = '{:,}'.format(transaction['amount'])
                    #
                    #         lbl3 = Button(self.canvas_frame, text=amount_nice, borderwidth=1, relief='sunken', padx=10, pady=3,
                    #                       command=lambda j=btn_string: copy_to_clipboard(self, j))
                    #         lbl3.grid(row=rows, column=2, padx=3, pady=3, sticky=NSEW)


                    # FINISH ME

    def copy_to_clipboard(self, data):
        logging.info('Copied data "{}" to clipboard.'.format(data))
        self.clipboard_clear()
        self.clipboard_append(data)
        self.update()
