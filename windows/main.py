from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from datetime import datetime, timedelta
from . import settings
from . import bgs
from . import timezone
from . import crime
from lib import debased
from lib import monitor

import logging
logger = logging.getLogger(__name__)


class MainWindow(Tk):
    """ Create main window """

    def __init__(self, config):
        logging.debug('Creating main window.')
        self.conf = config

        # Create window
        Tk.__init__(self)
        self.title(self.conf['theme']['titles']['main'])
        self.geometry("610x340")
        self.iconbitmap(self.conf['theme']['icon'])
        self.resizable(0,0)  # Disable resize
        self.rowconfigure(13, pad=10)
        self.columnconfigure(2, weight=5)
        self.protocol("WM_DELETE_WINDOW", self.shutdown)

        # Custom variables
        self.commander_name = StringVar()
        self.ship_name = StringVar()
        self.credits = StringVar()
        self.credits_int = 0
        self.credits_delta = StringVar()
        self.credits_delta_int = 0
        self.game_mode = StringVar()
        self.location = StringVar()
        self.advisor = StringVar()
        self.status_line = StringVar()
        self.clock_local = StringVar()
        self.clock_server = StringVar()
        self.countdown_board = StringVar()
        self.countdown_influence = StringVar()
        # self.session_stats = StringVar()

        # Establish DB, try to update strings from old data
        self.db = debased.Debaser()

        if not self.commander_name.get():
            logging.debug('Trying to load session data.')
            session = self.db.get_session()
            logging.debug('Setting strings to previous session data.')
            self.update_commander(session['commander_name'])
            self.update_shipname(session['ship_name'], session['ship'])
            self.credits.set(session['credits'])
            self.credits_int = session['credits_int']
            self.credits_delta.set('$0')
            self.update_game_mode(session['game_mode'], session['game_mode_group'])
            self.update_location(session['location'])
            self.set_status('Session data loaded.')

        self.monitor = monitor.JournalMonitor(self)
        self.monitor.start()

        # Menu bar configuration
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)

        # Main menu
        self.menu_main = Menu(self.menu_bar, tearoff=0)

        # This section includes/excludes menu features based on menus.yml. It's a bit messy. :(
        if self.conf['menu']['main']['settings']:
            self.menu_main.add_command(label="Settings", command=lambda: settings.SettingsWindow(self))
        self.menu_main.add_command(label="Check for updates", command=stub)
        if self.conf['menu']['main']['feature_request'] or self.conf['menu']['bug_report']:
            self.menu_main.add_separator()
        if self.conf['menu']['main']['feature_request']:
            self.menu_main.add_command(label="Request a feature", command=stub)
        if self.conf['menu']['main']['bug_report']:
            self.menu_main.add_command(label="Report a bug", command=stub)
        if self.conf['menu']['main']['credits']:
            self.menu_main.add_separator()
            self.menu_main.add_command(label="Credits", command=stub)
        if self.conf['menu']['main']:
            self.menu_main.add_separator()
            self.menu_main.add_command(label="Exit", command=self.shutdown)

        # Add menus to menu bar
        self.menu_bar.add_cascade(label="Menu", menu=self.menu_main)
        if self.conf['menu']['timezones']:
            self.menu_bar.add_command(label="Timezones", command=lambda: timezone.TZWindow(self))
        if self.conf['menu']['radio']:
            self.menu_bar.add_command(label=self.conf['theme']['menu']['radio'], command=stub)
        if self.conf['menu']['affiliate']:
            self.menu_bar.add_command(label=self.conf['theme']['menu']['affiliate'], command=stub)
        if self.conf['menu']['donate']:
            self.menu_bar.add_command(label=self.conf['theme']['menu']['donate'], command=stub)

        # Faction image
        self.faction_image_file = ImageTk.PhotoImage(Image.open(self.conf['theme']['logo']))
        self.faction_image = Label(self, image=self.faction_image_file)
        self.faction_image.grid(column=0, row=0, rowspan=9, columnspan=2, sticky=N)

        # Local clock
        if self.conf['menu']['clock_local']:
            self.text_clock_localtime = Label(self, text='Local time:')
            self.text_clock_localtime.grid(column=0, row=9, sticky=E)
            self.clock_localtime = Label(self, textvariable=self.clock_local)
            self.clock_localtime.grid(column=1, row=9, sticky=W)

        # Server clock
        if self.conf['menu']['clock_server']:
            self.text_clock_servertime = Label(self, text='Server time:')
            self.text_clock_servertime.grid(column=0, row=10, sticky=E)
            self.clock_servertime = Label(self, textvariable=self.clock_server)
            self.clock_servertime.grid(column=1, row=10, sticky=W)

        # Board countdown
        if self.conf['menu']['countdown_board']:
            self.clock_countdown_board = Label(self, textvariable=self.countdown_board)
            self.clock_countdown_board.grid(column=0, columnspan=2, row=11, sticky=W+E)

        # Influence tick countdown
        if self.conf['menu']['countdown_influence']:
            self.clock_countdown_influence = Label(self, textvariable=self.countdown_influence)
            self.clock_countdown_influence.grid(column=0, columnspan=2, row=12, sticky=W+E)

        # Session text frame creation
        self.frame_session = ttk.Frame()
        self.frame_session.grid(column=2, row=0, rowspan=12, columnspan=5, sticky="N,W,E,S", padx=3, pady=3)
        self.frame_session.columnconfigure(1, weight=1)
        self.frame_session.columnconfigure(3, weight=1)
        self.frame_session.rowconfigure(10, weight=5)

        # Commander name
        self.session_stats_name = Label(self.frame_session, justify=CENTER, textvariable=self.commander_name)
        self.session_stats_name.grid(column=0, row=0, columnspan=8, sticky=NSEW)
        self.session_stats_name.grid_propagate(False)

        # Ship name
        self.text_session_stats_ship = Label(self.frame_session, justify=LEFT, text='Ship:')
        self.text_session_stats_ship.grid(column=0, row=1, sticky=E)
        self.session_stats_ship = Label(self.frame_session, justify=LEFT, textvariable=self.ship_name)
        self.session_stats_ship.grid(column=1, row=1, sticky=W)
        self.session_stats_ship.grid_propagate(False)

        # Location
        self.text_session_stats_location = Label(self.frame_session, justify=LEFT, text='Location:')
        self.text_session_stats_location.grid(column=0, row=7, columnspan=1,  rowspan=1, sticky=E)
        self.session_stats_location = Label(self.frame_session, justify=LEFT, textvariable=self.location, wraplength=300)
        self.session_stats_location.grid(column=1, row=7, columnspan=4, rowspan=1, sticky=W)
        self.session_stats_location.grid_propagate(False)

        # Credits
        self.text_session_stats_credits = Label(self.frame_session, justify=LEFT, text='Credits:')
        self.text_session_stats_credits.grid(column=0, row=2, sticky=E)
        self.session_stats_credits = Label(self.frame_session, justify=LEFT, textvariable=self.credits)
        self.session_stats_credits.grid(column=1, row=2, sticky=W)
        self.session_stats_credits.grid_propagate(False)

        # Credits Delta (Lost/Earned)
        self.text_session_stats_creditDelta = Label(self.frame_session, justify=LEFT, text='Profit/Loss:')
        self.text_session_stats_creditDelta.grid(column=0, row=4, sticky=E)
        self.session_stats_creditDelta = Label(self.frame_session, justify=LEFT, textvariable=self.credits_delta)
        self.session_stats_creditDelta.grid(column=1, row=4, sticky=W)
        self.session_stats_creditDelta.grid_propagate(False)

        # Game Mode
        self.text_session_stats_mode = Label(self.frame_session, justify=LEFT, text='Game Mode:')
        self.text_session_stats_mode.grid(column=0, row=6, sticky=E)
        self.session_stats_mode = Label(self.frame_session, justify=LEFT, textvariable=self.game_mode, wraplength=300)
        self.session_stats_mode.grid(column=1, row=6, columnspan=4, sticky=W)
        self.session_stats_mode.grid_propagate(False)

        # Advisor
        if self.conf['settings']['show_advisor']:
            self.text_advisor = Label(self.frame_session, justify=LEFT, text='Advisor:')
            self.text_advisor.grid(column=0, row=10, sticky=E)
            self.advisor_label = Label(self.frame_session, justify=LEFT, textvariable=self.advisor, wraplength=300)
            self.advisor_label.grid(column=1, row=10, columnspan=4, sticky=W)
            self.advisor_label.grid_propagate(False)

        # Frame for status bar
        self.status_frame = ttk.Frame(self, borderwidth=2, relief=SUNKEN)
        self.status_frame.grid(column=0, row=13, columnspan=3, rowspan=2, sticky=N+W+E+S, pady=5)
        self.status_frame.rowconfigure(0, weight=2)
        self.status_frame.rowconfigure(1, weight=2)
        self.status_frame.columnconfigure(0, weight=2)

        # Status bar
        self.status_bar = Label(self.status_frame, textvariable=self.status_line, justify=LEFT, anchor=W, wraplength=590)
        self.status_bar.grid(column=0, row=0, sticky=W)
        self.status_bar.grid_propagate(False)
        self.buffer_lbl = ttk.Label(self.status_frame, text='\n', justify=LEFT, anchor=W)
        self.buffer_lbl.grid(column=0, row=1, sticky=W)

        # Arbitrarily stick button on there somewhere
        self.buttons_frame = ttk.Frame(self, padding="3 3 3 3")
        self.buttons_frame.grid(sticky="E,S,W")
        self.buttons_frame.rowconfigure(0)
        self.buttons_frame.place(y=230, x=410)

        self.button_view_bgs = ttk.Button(
            self.buttons_frame, text='View BGS Stats', command=lambda: bgs.BgsWindow(self)
        )
        self.button_view_bgs.grid(column=2, row=3)

        self.button_view_bgs = ttk.Button(
            self.buttons_frame, text='View Crime Report', command=lambda: crime.CrimeWindow(self)
        )
        self.button_view_bgs.grid(column=1, row=3)

        self.update_clock_times()
        logging.debug('Main window drawn.')

    def shutdown(self):
        logging.info('Shutting down.')
        print(str(self.db.get_session()))
        self.monitor.stop()
        self.monitor.join()
        self.db.close()
        self.destroy()

    def set_status(self, text):
        """ Method to update the status line """

        time = datetime.strftime(datetime.now(), "%H:%M:%S - ")

        logging.debug('Updating status line with "' + time + text + '"')
        self.status_line.set(time + text)

    def update_credits(self, amount):
        """ Method to update displayed credits, returning nice readable strings """

        logging.debug('Updating credits.')
        old_total = self.credits_int
        if amount != 0:
            if amount > 0:
                self.credits_int + amount
                self.credits_delta_int + amount
                logging.debug('Added {} credits to previous total of {}. New total: {}. Delta: {}'.format(
                    amount, old_total, self.credits_int, self.credits_delta_int
                ))
            elif amount < 0:
                self.credits_int - amount
                self.credits_delta_int - amount
                logging.debug('Removing {} credits from previous total of {}. New total: {}. Delta: {}'.format(
                    amount, old_total, self.credits_int, self.credits_delta_int
                ))
            # Format the credit strings nicely
            logging.debug('Updating credits.')
            nice_credits = str('${:,}'.format(self.credits_int))
            nice_delta = str('${:,}'.format(self.credits_delta_int))
            self.credits.set(nice_credits)
            self.credits_delta.set(nice_delta)
            logging.debug('Credits stored.')
            session = {'credits': nice_credits, 'credits_int': amount}
            self.db.update_session(session)
        else:
            logging.debug('Received no credits for this transaction.')

    def update_location(self, location):
        """ Update the displayed current location """

        if location != self.location.get():
            logging.debug('Updating location to "{}"'.format(location))
            logging.debug('Previous location: "{}"'.format(self.location.get()))
            self.location.set(location)
            logging.debug('Location set.')
            session = {'location': location }
            self.db.update_session(session)
            logging.debug('Location stored.')

        else:
            logging.debug('Attempted to update location, but was identical to existing record.')

    def update_shipname(self, name, ship):
        """ Update the displayed ship name """

        if len(ship) > 0:
            name = '{} [{}]'.format(name, ship)

        if name != self.ship_name.get():
            logging.debug('Updating ship name to "{}"'.format(name))
            logging.debug('Previous ship name: "{}"'.format(self.ship_name.get()))
            self.ship_name.set(name)
            logging.debug('Ship name set.')
            session = {'ship_name': name, 'ship': ship}
            self.db.update_session(session)
            logging.debug('Ship name and type stored.')
        else:
            logging.debug('Attempted to update ship name, but was identical to existing record.')

    def update_commander(self, name):
        """ Update the displayed commander name """

        if name != self.commander_name.get():
            logging.debug('Updating commander\'s name to "{}"'.format(name))
            logging.debug('Previous commander\'s name: "{}"'.format(self.commander_name.get()))
            self.commander_name.set(name)
            logging.debug('Commander\'s name set.')
            session = {'commander_name': name}
            self.db.update_session(session)
            logging.debug('Commander\'s name stored.')
        else:
            logging.debug('Attempted to update the commander\'s name, but was identical to existing record.')

    def update_game_mode(self, mode, *group):
        """ Update the displayed game mode """

        if 'group' in locals():
            if len(group) > 1:
                mode = '{} ({})'.format(mode, group)
        if mode != self.game_mode.get():
            logging.debug('Updating game mode to "{}"'.format(mode))
            logging.debug('Previous game mode: "{}"'.format(self.game_mode.get()))
            self.game_mode.set(mode)
            logging.debug('Game mode set.')
            session = {'game_mode': mode,
                                   'group': group}
            self.db.update_session(session)
            logging.debug('Game mode stored.')
        else:
            logging.debug('Attempted to update the game mode, but was identical to existing record.')

    def update_advisor(self, advice):
        """ Log and update changes to the advisor text """

        if advice != self.advisor.get():
            logging.debug('Updating advisor text to "{}"'.format(advice))
            logging.debug('Previous advice: "{}"'.format(self.advisor.get()))
            self.advisor.set(advice)
            logging.debug('Game mode set.')
        else:
            logging.debug('Attempted to update the game mode, but was identical to existing record.')

    def update_clock_times(self):
        """ Update clocks and countdowns """
        try:
            now = datetime.now()
            utc = datetime.utcnow()

            # Update clocks
            self.clock_local.set(datetime.strftime(now, "%H:%M:%S"))
            self.clock_server.set(datetime.strftime(utc, "%H:%M:%S"))

            # Update influence countdown.
            influence_processing_start = utc.replace(
                hour=datetime.strptime(self.conf['bgs']['inf_tick_start'], '%H:%M').hour,
                minute=datetime.strptime(self.conf['bgs']['inf_tick_start'], '%H:%M').minute
            )
            influence_processing_end = utc.replace(
                hour=datetime.strptime(self.conf['bgs']['inf_tick_end'], '%H:%M').hour,
                minute=datetime.strptime(self.conf['bgs']['inf_tick_end'], '%H:%M').minute
            )

            if utc > influence_processing_end:  # Influence has already been processed today, calc time until tomorrow
                try:
                    influence_processing_start = influence_processing_start.replace(
                        day=influence_processing_start.day + 1
                    )
                except ValueError:
                    influence_processing_start = influence_processing_start.replace(
                        day=1,
                        month=influence_processing_start.month + 1
                    )
                    pass

            delta = influence_processing_start - utc

            if utc < influence_processing_start: # Influence window has yet to occur
                remaining_hours = delta.seconds / 3600
                if remaining_hours >= 1.2:
                    self.countdown_influence.set('Influence tick begins in around {} hours.'.format(
                        str(remaining_hours)[0:2])
                    )
                elif remaining_hours < 1.2 and remaining_hours > 1:
                    self.countdown_influence.set('Influence tick begins in around an hour.')
                elif remaining_hours < 1 and remaining_hours > 0.5:
                    self.countdown_influence.set('Influence tick begins in less than an hour.')
                elif remaining_hours < 0.15:
                    self.countdown_influence.set('Influence tick begins shortly.')
            elif utc > influence_processing_start and utc < influence_processing_end: # Influence is calculating now
                self.countdown_influence.set('Influence is currently being calculated.')
        except:
            logging.exception('Caught exception during influence tick.')
            self.countdown_influence.set('Time until influence tick unknown.')
            pass

        ''' 
        Update mission board countdown (for board flippers).
        This is generally understood to occur every 15 minutes or so, however the player won't notice any changes
        unless they actually change game modes, etc.
            FDev, please make mission boards suck less.
                    Kind Regards,
                    - Everybody

        Stolen from https://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object-python
        (Yes, I'm bad at math - BC)
        '''

        try:
            discard = timedelta(minutes=utc.minute % 15,
                                seconds=utc.second,
                                microseconds=utc.microsecond)

            # Get time until next interval
            rounded = utc - discard
            if discard <= timedelta(minutes=15):
                rounded += timedelta(minutes=15)
            final = rounded - utc
            seconds_total = final.total_seconds()
            minutes = int((seconds_total % 3600) / 60)
            seconds = int(seconds_total % 60)

            if minutes > 1:
                self.countdown_board.set('Boards refresh in {} minutes.'.format(minutes))
            if minutes == 1:
                self.countdown_board.set('Boards refresh in {} minute, {} seconds.'.format(minutes, seconds))
            elif minutes < 1:
                self.countdown_board.set('Boards refresh in {} seconds.'.format(seconds))
        except:
            logging.exception('Exception occured updating board refresh.')
            self.countdown_board.set('Time until board refresh unknown.')

        self.after(1000, self.update_clock_times)


    # def monitor_queue(self):
    #     """
    #     This monitors the queue and executes actions that update the GUI when certain conditions are met.
    #     Predominately this is just updating elements like the status bar.
    #     """
    #     try:
    #         item = self.queue.get(block=False)
    #     except:  # queue.Empty:
    #         pass
    #     else:
    #         try:
    #             if item['type'] == 'name':
    #                 self.update_commander(item['value'])
    #             elif item['type'] == 'credits':
    #                 self.update_credits(item['value'])
    #             elif item['type'] == 'mode':
    #                 self.update_game_mode(item['value'])
    #             elif item['type'] == 'location':
    #                 self.update_location(item['value'])
    #             elif item['type'] == 'advisor':
    #                 self.update_advisor(item['value'])
    #         except KeyError:
    #             logging.warning('Window queue received a packet that it doesn\'t subscribe to: ' + str(item))
    #             pass
    #
    #     self.after(100, self.monitor_queue)


def stub():
    pass


