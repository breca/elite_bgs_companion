'''
Main Window

Copyright (C) 2018, CMDR Kalis for Radio Sidewinder.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from sys import exit
from time import sleep
import datetime as dt
import json
import threading, queue
from os import environ, path
import glob
from pytz import timezone
from collections import defaultdict
import sqlite3
import random
import copy
import configparser
from lib import bucket
from lib import log
from lib import db
from lib.window_bgs import window_bgs
from lib.window_credits import window_credits
from lib.window_feature_req import window_feature_req
from lib.window_report_bug import window_report_bug
from lib.window_options import window_options
from lib.advisor import advisor
from lib import links
from lib import version_checker
from lib import eddn_sender
from lib import commodities

config = configparser.ConfigParser()
config.read('settings.ini')

def main():
    '''###########################################
    #                startup
    ###########################################'''

    # Generic config
    global runtime
    runtime = { 'logged_in': False,
               'name_set' : False,
               'stats_set': False,
               'advisor_init' : False,
               'commander_name': 'Loading...',
               'commander_tz': '',
               'credits': 'Waiting',
               'credits_start': 'Waiting',
               'ship_name': 'Waiting',
               'ship': '',
               'game_mode': 'Unavailable',
               'game_mode_group': '',
               'flight': '(Placeholder)',
               'flight_rank': '(Placeholder)',
               'player_faction_online': 0,
               'star_system': 'unknown',
               'system_is_target_faction_owned': False,
               'system_pop': '',
               'near_body': '',
               'near_body_type': '',
               'docked': '',
               'landed': '',
               'station_name': '',
               'target_faction': '',
               'station_faction': '',
               'target_faction_state': '',
               'old_target_faction_state': 'Nil',
               'location': '',
               'in_srv': '',
               'jump_type': '',
               'journal_path': path.join(environ.get("USERPROFILE") + '\\Saved Games\\Frontier Developments\\Elite Dangerous'),
               'journal_file': '',
               'journal_byte_offset': 0
               }
    runtime['target_faction'] = config['General']['AdvisorFaction']
    runtime['log_level'] =  config['General']['LogLevel']

    if config['General']['override_journal_location']:
        log.info('Overriding default journal location with "{}"'.format(config['General']['override_journal_location']))
        runtime['journal_path'] = config['General']['override_journal_location']

    log.info('Started.')

    '''###########################################
    #             window config
    ###########################################'''

    # Create main window
    root = Tk()
    root.title("BGS Companion")
    root.geometry("610x340")
    root.iconbitmap(r'images\favicon.ico')
    root.resizable(0,0) #Disable resize
    root.rowconfigure(13, pad=10)
    root.columnconfigure(2, weight=5)

    # Define vars
    global status_line
    global local_clock
    global server_clock
    global board_countdown
    global tick_countdown
    global session_stats
    status_line = StringVar()

    '''-----------------------------------------'''

    # Top menu bars
    menu_bar = Menu(root)
    root.config(menu=menu_bar)

    # 'Menu' menu
    menu_file = Menu(menu_bar,tearoff=0)

    # 'About' menu
    menu_main = Menu(menu_bar,tearoff=0)

    menu_main.add_command(label="Settings", command=lambda: window_options(root, config))
    menu_main.add_command(label="Check for updates", command=lambda: check_version(root, msg_queue, config, True))
    menu_main.add_separator()
    menu_main.add_command(label="Request a feature", command=lambda: window_feature_req(root))
    menu_main.add_command(label="Report a bug", command=lambda: window_report_bug(root))
    menu_main.add_separator()
    menu_main.add_command(label="Credits", command=lambda: window_credits(root))
    menu_main.add_separator()
    menu_main.add_command(label="Exit", command=lambda: graceful_close(root, monitor_data, monitor_status, monitor_journal, eddn_dispatcher))

    # Add menus to menu bar
    menu_bar.add_cascade(label="Menu", menu=menu_main)
    menu_bar.add_command(label="Timezones", command=window_timezones)
    menu_bar.add_command(label="Radio", command=lambda: links.listen(config))
    menu_bar.add_command(label="Buy Skins", command=lambda: links.skin(config))
    menu_bar.add_command(label="Donate", command=lambda: links.donate(config))


    '''-----------------------------------------'''

    # Faction image to left
    icon_image = ImageTk.PhotoImage(Image.open('images\logo_patch.png'))
    ic = Label(root, image=icon_image)
    ic.grid(column=0, row=0, rowspan=9, columnspan=2, sticky=N)


    '''-----------------------------------------'''

    # Local clock text
    local_clock_text = Label(root, text='Local time:')
    local_clock_text.grid(column=0, row=9, sticky=E)
    # local clock
    local_clock = Label(root)
    local_clock.grid(column=1, row=9, sticky=W)
    time_local()

    # server clock text
    server_clock_text = Label(root, text='Server time:')
    server_clock_text.grid(column=0, row=10, sticky=E)
    # server clock
    server_clock = Label(root)
    server_clock.grid(column=1, row=10, sticky=W)
    time_server()

    # board countdown
    board_countdown = Label(root)
    board_countdown.grid(column=0, columnspan=2, row=11, sticky=W+E)
    tick_board()

    # influence tick countdown
    tick_countdown = Label(root)
    tick_countdown.grid(column=0, columnspan=2, row=12, sticky=W+E)
    tick_server(config)

    '''-----------------------------------------'''

    global stats
    stats = {
        'name': StringVar(),
        'flight': StringVar(),
        'rank': StringVar(),
        'ship': StringVar(),
        'location': StringVar(),
        'credits': StringVar(),
        'creditDelta': StringVar(),
        'player_faction_online': StringVar(),
        'gameMode': StringVar(),
        'advice': StringVar()
        }

    stats['name'].set('Loading...')

    # Session text creation
    session_frame = Frame(root)
    session_frame.grid(column=2, row=0, rowspan=12, columnspan=5, sticky="N,W,E,S", padx=3, pady=3)
    session_frame.columnconfigure(1, weight=1)
    session_frame.columnconfigure(3, weight=1)
    session_frame.rowconfigure(10, weight=5)

    session_stats_name_text = Label(session_frame, justify=CENTER, textvariable=stats['name'])
    session_stats_name_text.grid(column=0, row=0, columnspan=8, sticky=NSEW)
    session_stats_name_text.grid_propagate(False)

    # session_stats_flight_text = Label(session_frame, justify=LEFT, text='Flight:')
    # session_stats_flight_text.grid(column=0, row=1, sticky=E)
    # session_stats_flight = Label(session_frame, justify=LEFT, textvariable=stats['flight'])
    # session_stats_flight.grid(column=1, row=1, columnspan=10, sticky=W)
    # session_stats_flight.grid_propagate(False)
    #
    # session_stats_rank_text = Label(session_frame, justify=LEFT, text='Rank:')
    # session_stats_rank_text.grid(column=0, row=2, sticky=E)
    # session_stats_rank = Label(session_frame, justify=LEFT, textvariable=stats['rank'])
    # session_stats_rank.grid(column=1, row=2, sticky=W)
    # session_stats_rank.grid_propagate(False)

    # session_stats_rsc_text = Label(session_frame, justify=LEFT, text='RSC in-game:')
    # session_stats_rsc_text.grid(column=0, row=4, sticky=E)
    # session_stats_rsc = Label(session_frame, justify=LEFT, textvariable=stats['rsc'])
    # session_stats_rsc.grid(column=1, row=4, sticky=W)
    # session_stats_rsc.grid_propagate(False)

    session_stats_ship_text = Label(session_frame, justify=LEFT, text='Ship:')
    session_stats_ship_text.grid(column=0, row=1, sticky=E)
    session_stats_ship = Label(session_frame, justify=LEFT, textvariable=stats['ship'])
    session_stats_ship.grid(column=1, row=1, sticky=W)
    session_stats_ship.grid_propagate(False)

    session_stats_location_text = Label(session_frame, justify=LEFT, text='Location:')#, anchor=E)
    session_stats_location_text.grid(column=0, row=7, columnspan=1,  rowspan=1, sticky=E)
    session_stats_location = Label(session_frame, justify=LEFT, textvariable=stats['location'], wraplength=300)#, anchor=W)
    session_stats_location.grid(column=1, row=7, columnspan=4, rowspan=1, sticky=W)
    session_stats_location.grid_propagate(False)

    session_stats_credits_text = Label(session_frame, justify=LEFT, text='Credits:')
    session_stats_credits_text.grid(column=0, row=2, sticky=E)
    session_stats_credits = Label(session_frame, justify=LEFT, textvariable=stats['credits'])
    session_stats_credits.grid(column=1, row=2, sticky=W)
    session_stats_credits.grid_propagate(False)

    session_stats_creditDelta_text = Label(session_frame, justify=LEFT, text='Profit/Loss:')
    session_stats_creditDelta_text.grid(column=0, row=4, sticky=E)
    session_stats_creditDelta = Label(session_frame, justify=LEFT, textvariable=stats['creditDelta'])
    session_stats_creditDelta.grid(column=1, row=4, sticky=W)
    session_stats_creditDelta.grid_propagate(False)

    session_stats_gameMode_text = Label(session_frame, justify=LEFT, text='Game Mode:')
    session_stats_gameMode_text.grid(column=0, row=6, sticky=E)
    session_stats_gameMode = Label(session_frame, justify=LEFT, textvariable=stats['gameMode'], wraplength=300)
    session_stats_gameMode.grid(column=1, row=6, columnspan=4, sticky=W)
    session_stats_gameMode.grid_propagate(False)

    session_stats_gameMode_text = Label(session_frame, justify=LEFT, text='Advisor:')
    session_stats_gameMode_text.grid(column=0, row=10, sticky=E)
    session_stats_gameMode = Label(session_frame, justify=LEFT, textvariable=stats['advice'], wraplength=300)
    session_stats_gameMode.grid(column=1, row=10, columnspan=4, sticky=W)
    session_stats_gameMode.grid_propagate(False)

    '''-----------------------------------------'''

    # bottom status bar
    status_frame = Frame(root, borderwidth=2, relief=SUNKEN)
    status_frame.grid(column=0, row=13, columnspan=3, rowspan=2, sticky=N+W+E+S, pady=5)
    status_frame.rowconfigure(0, weight=2)
    status_frame.rowconfigure(1, weight=2)
    status_frame.columnconfigure(0, weight=2)

    status_bar = ttk.Label(status_frame, textvariable=status_line, justify=LEFT, anchor=W, wraplength=590)
    status_bar.grid(column=0, row=0, sticky=W)#place(x=3, rely=0.86, width=600)
    status_bar.grid_propagate(False)
    buffer_lbl = ttk.Label(status_frame, text='\n', justify=LEFT, anchor=W)
    buffer_lbl.grid(column=0, row=1, sticky=W)

    buttons_frame = ttk.Frame(root, padding="3 3 3 3",)#, padding="200 3 200 3")
    buttons_frame.grid(sticky="N,E,S,W")
    buttons_frame.rowconfigure(0)#, weight=2)
    buttons_frame.place(y=230,x=510)#relx=0.32)
    button_view_bgs = ttk.Button(buttons_frame, text='View BGS Stats', command=lambda: window_bgs(root, monitor_data, runtime))
    button_view_bgs.grid(column=1, row=3)


    '''###########################################
    #                threading
    ###########################################'''

    # setup and start threads (if not already started)
    data_queue = queue.Queue()
    msg_queue = queue.Queue()
    monitor_data = DataBroker(msg_queue, data_queue)
    monitor_status = MessageMonitor(msg_queue)
    monitor_journal = JournalMonitor(msg_queue, data_queue)
    eddn_dispatcher = eddn_sender.EDDN_dispatcher(runtime['journal_path'], config)
    start_threads(monitor_data, monitor_status, monitor_journal, eddn_dispatcher)


    '''###########################################
    #                main loop
    ###########################################'''

    def session_updater():
        session_stats_update()
        root.after(300, session_updater)

    root.protocol("WM_DELETE_WINDOW", lambda: graceful_close(root, monitor_data, monitor_status, monitor_journal, eddn_dispatcher))
    root.after(300, session_updater)
    root.after(2000, lambda: check_version(root, msg_queue, config))
    root.mainloop()


# check for updates
def check_version(window, msg_queue, config, *force):
    if force:
        version_checker.check(window, msg_queue, config, force)
    else:
        version_checker.check(window, msg_queue, config)

# timezone window
def window_timezones():
    log.info('Opening timezone window.')
    win = Tk()
    win.iconbitmap(r'images\favicon.ico')
    win.title('Timezones')
    tz_frame = ttk.Frame(win, padding="5 5 5 20")
    tz_frame.grid()

    timezones = { 'Australia, Eastern: ': timezone('Australia/Sydney'),
                  'Australia, Western: ': timezone('Australia/Perth'),
                  'Germany: ': timezone('Europe/Berlin'),
                  'Russia, Eastern: ': timezone('Asia/Vladivostok'),
                  'Russia, Western: ': timezone('Europe/Moscow'),
                  'United Kingdom: ': timezone('Europe/London'),
                  'United States, EST: ': timezone('America/New_York'),
                  'United States, PST: ': timezone('America/Los_Angeles')
                }

    time = dt.datetime.strftime(dt.datetime.now(), '%H:%M')

    text = 'Times around the world as of {} local time:'.format(time)

    top_lbl = Label(tz_frame, padx=5, pady=10, text=text)
    top_lbl.grid(row=0, column=0, columnspan=2)
    rows = 1
    for place in timezones.keys():
        plc_lbl = Label(tz_frame, text=place, justify=RIGHT)
        plc_lbl.grid(row=rows, column=0, sticky=E)
        tm = dt.datetime.strftime(dt.datetime.now(timezones[place]), '%A, %H:%M')
        tm_lbl = Label(tz_frame, text=tm)
        tm_lbl.grid(row=rows, column=1)
        rows+=1
    invis = Label(tz_frame, text='   ')
    invis.grid(row=rows, column=0, columnspan=2, sticky=S)
    rows+=1
    tz_button = Button(tz_frame, padx=20, pady=5, command=win.destroy, text='Ok', anchor=S)
    tz_button.grid(row=rows, column=0, columnspan=2, sticky=S)



'''###########################################
#       statistic update functions
###########################################'''

# update main window's session stats
def session_stats_update():
    #log.debug('Session statistics are being updated')
    try:
        if runtime['stats_set']:
            # choose a random greeting
            #log.debug('Assigning statistics to values.')
            greet_text = ['Welcome, Commander ', 'Good to see you, Commander ', 'Commander ', 'Lets get to work, Commander ']
            if not runtime['name_set']:
                stats['name'].set(random.choice(greet_text) + runtime['commander_name'] + '.')
                runtime['name_set'] = True
            # stats['flight'].set('Stub') #FIXME with real data
            # stats['rank'].set('Stub')   #FIXME with real data
            stats['ship'].set('{} ({})'.format(runtime['ship_name'],runtime['ship']))
            stats['location'].set(location_parse())
            stats['credits'].set(str('{:,}'.format(runtime['credits'])))
            stats['creditDelta'].set(credit_delta())
            # stats['rsc'].set('Stub') #FIXME with real data
            if runtime['target_faction_state'] != runtime['old_target_faction_state'] or not runtime['advisor_init']:
                stats['advice'].set(advisor_state_flavour_text())
            if runtime['game_mode'] == 'Group':
                stats['gameMode'].set('Private Group (' + runtime['game_mode_group'] + ')')
            else:
                stats['gameMode'].set(runtime['game_mode'])
        else:
            stats['name'].set(runtime['commander_name'])

    except Exception as e:
        log.exception('Exception occured refreshing main window stat string variables.', e)
        pass


# make some nice location text
def location_parse():
    #log.debug('Formatting location string.')
    if runtime['star_system']:
        if runtime['docked']:
            if runtime['station_faction'] == runtime['target_faction']:
                runtime['location'] = 'Docked at {} station {} in the {} system.'.format(runtime['target_faction'], runtime['station_name'], runtime['star_system'])
                return runtime['location']
            else:
                runtime['location'] = 'Docked at {} in the {} system.'.format(runtime['station_name'], runtime['star_system'])
                return runtime['location']
        elif runtime['landed']:
            if runtime['near_body']: #and runtime['near_body_type'] == 'Planet':   #REVIEW
                if not runtime['in_srv']:
                    runtime['location'] = 'Landed on {} in the {} system.'.format(runtime['near_body'], runtime['star_system'])
                else:
                    runtime['location'] = 'In an SRV on {} in the {} system.'.format(runtime['near_body'], runtime['star_system'])
                return runtime['location']
        elif runtime['near_body'] and not runtime['docked'] or runtime['landed'] or runtime['in_srv']:
            runtime['location'] = 'In the {} system, near {}.'.format(runtime['star_system'], runtime['near_body'])
            return runtime['location']
            if runtime['station_name']:
                runtime['location'] = 'In the {} system, near {}.'.format(runtime['star_system'], runtime['station_name'])
                return runtime['location']
        else:
            runtime['location'] = 'In the {} system.'.format(runtime['star_system'])
            return runtime['location']
    else:
        runtime['location'] = 'Lost in space!'
        return runtime['location']


#determine session credit delta, return nice string
def credit_delta():
    nice_string = 0
    if runtime['credits'] >0 and runtime['credits_start'] == 'Waiting':
        log.info('Credits set.')
        runtime['credits_start'] = runtime['credits']
    elif isinstance(runtime['credits_start'], int):
        #log.debug('Credit delta measuring {} - {}'.format(runtime['credits'], runtime['credits_start']))
        delta = int(runtime['credits']) - int(runtime['credits_start'])
        nice_string = str('{:,}'.format(delta))
    return nice_string


# message bar updater for target_faction vouchers/missions
def voucher_tracker(update, msg_queue):
    log.debug('Voucher tracker called :' + str(update))
    #log.debug('Voucher tracker current runtime :' + str(update))
    if runtime['stats_set']:
        if 'voucher' in update.keys():
            log.debug('Voucher tracker processing voucher for {}.'.format(runtime['station_name']))
            if update['voucher']['type'] in ['bounty', 'CombatBond']:
                if update['voucher']['type'] == 'bounty':
                    start_msg = 'You redeemed bounties '
                elif update['voucher']['type'] == 'CombatBond':
                    start_msg = 'You redeemed combat bonds '
                factions = []
                for list_entry in update['voucher']['factions']: ##[['Radio Sidewinder Crew', 5009086]]
                    runtime['credits'] += list_entry[-1]
                    nice_amount = '{:,}'.format(list_entry[-1])
                    mid_msg = '({}, {} credits) '.format(list_entry[0], nice_amount)
                    start_msg = start_msg + mid_msg
                    if update['voucher']['valid'] == 'increase':
                        end_msg = start_msg + 'at {} in the {} system, prolonging the state of {}.'.format(runtime['station_name'], runtime['star_system'], runtime['station_faction_state'])
                    elif update['voucher']['valid'] == 'decrease':
                        end_msg = start_msg + 'at {} in the {} system, expediting the end of the {}.'.format(runtime['station_name'], runtime['star_system'], runtime['station_faction_state'])
                    elif update['voucher']['valid'] == 'valid':
                        end_msg = start_msg + 'at {} in the {} system.'.format(runtime['station_name'], runtime['star_system'] )
            # elif update['voucher']['type'] == 'CombatBond':
            #     msg_type = 'redeemed combat bonds worth'
            else:
                if update['voucher']['type'] == 'scannable' or update['voucher']['type'] == 'settlement':
                    msg_type = 'redeemed data worth'
                    nice_amount = str('{:,}'.format(update['voucher']['factions'][0][-1]))
                if update['voucher']['type'] == 'exploration':
                    msg_type = 'redeemed exploration data worth'
                elif update['voucher']['type'] == 'trade':
                    if update['voucher']['profit_made'] == True:
                        msg_type = 'traded goods and made a profit of'
                        runtime['credits'] += update['voucher']['amount']
                    if update['voucher']['profit_made'] == False:
                        msg_type = 'traded goods and suffered a loss of'
                        runtime['credits'] -= update['voucher']['amount']
                elif update['voucher']['type'] == 'smuggled':
                    if update['voucher']['profit_made'] == True:
                        msg_type = 'smuggled goods and made a profit of'
                        runtime['credits'] += update['voucher']['amount']
                    if update['voucher']['profit_made'] == False:
                        msg_type = 'smuggled goods and suffered a loss of'
                        runtime['credits'] -= update['voucher']['amount']
                if not 'nice_amount' in locals():
                    nice_amount = str('{:,}'.format(update['voucher']['amount']))

                if update['voucher']['valid'] == 'increase':
                    end_msg = 'You {} {} credits for {} at {} in the {} system, prolonging the state of {}.'.format(msg_type, nice_amount, runtime['station_faction'], runtime['station_name'], runtime['star_system'], runtime['station_faction_state'])
                elif update['voucher']['valid'] == 'decrease':
                    end_msg = 'You {} {} credits for {} at {} in the {} system, expediting the end of the {}.'.format(msg_type, nice_amount, runtime['station_faction'], runtime['station_name'], runtime['star_system'], runtime['station_faction_state'])
                elif update['voucher']['valid'] == 'valid':
                    end_msg = 'You {} {} credits for {} at {} in the {} system.'.format(msg_type, nice_amount, runtime['station_faction'], runtime['station_name'], runtime['star_system'])

                #trade credits are handled seperately
                if update['voucher']['type'] not in ['trade', 'smuggle', 'scannable', 'settlement']:
                    runtime['credits'] += update['voucher']['amount']

        if 'mission' in update.keys():
            log.debug('Voucher tracker processing mission.')
            if update['mission']['status'] == 'accepted':
                if update['mission']['type'] == 'donation':
                    end_msg = 'You accepted a request to donate credits to {} at {} in the {} system.'.format(update['mission']['faction'], runtime['station_name'], runtime['star_system'])
                if update['mission']['type'] == 'mission':
                    end_msg = 'You accepted a mission for {} at {} in the {} system.'.format(update['mission']['faction'], runtime['station_name'], runtime['star_system'])
            elif update['mission']['status'] == 'completed':
                nice_amount = str('{:,}'.format(update['mission']['amount']))
                if update['mission']['type'] == 'donation':
                    end_msg = 'You donated {} credits to {} at {} in the {} system.'.format(nice_amount, update['mission']['mission_giver_faction'], update['mission']['mission_giver_station'], update['mission']['mission_giver_system'])
                    runtime['credits'] -= update['mission']['amount']
                if update['mission']['type'] == 'mission':
                    end_msg = 'You completed a mission and raised {} credits for {} at {} in the {} system.'.format(nice_amount, update['mission']['mission_giver_faction'], update['mission']['mission_giver_station'], update['mission']['mission_giver_system'])
                    runtime['credits'] += update['mission']['amount']
        if 'end_msg' in locals():
            log.info('Voucher tracker updating status bar with: ' + end_msg)
            msg_queue.put(end_msg)
        else:
            log.debug('Voucher tracker was somehow given bad info. No updates pushed.')
    else:
        msg_queue.put('Loading, please wait...')






'''###########################################
#             clocks
###########################################'''


# local time clock for main window
def time_local():
    # get the current local time from the PC
    time = dt.datetime.now()
    time_string = dt.datetime.strftime(time, '%H:%M:%S')

    # if time string has changed, update it
    local_clock.config(text=time_string)
    local_clock.after(300, time_local)



# server time clock for main window
def time_server():
    # get the current local time from the PC
    time = dt.datetime.utcnow()
    time_string = dt.datetime.strftime(time, '%H:%M:%S')

    # if time string has changed, update it
    server_clock.config(text=time_string)
    server_clock.after(300, time_server)


# board countdown timer for main window
def tick_board():
    utc = dt.datetime.utcnow()
    discard = dt.timedelta(minutes=utc.minute % 15,
                        seconds=utc.second,
                        microseconds=utc.microsecond)
    # Get time until next interval
    rounded = utc - discard
    if discard <= dt.timedelta(minutes=15):
        rounded += dt.timedelta(minutes=15)
    final = rounded - utc
    seconds_total = final.total_seconds()
    minutes = int((seconds_total % 3600) / 60)
    seconds = int(seconds_total % 60)

    if minutes > 1:
        countdown = 'Boards refresh in {} minutes.'.format(minutes)
    if minutes == 1:
        countdown = 'Boards refresh in {} minute, {} seconds.'.format(minutes, seconds)
    elif minutes < 1:
        countdown = 'Boards refresh in {} seconds.'.format(seconds)

    # if time string has changed, update it
    board_countdown.config(text=countdown)
    board_countdown.after(300, tick_board)


# influence tick countdown timer for main window
def tick_server(config):
    try:
        """ Update clocks and countdowns """
        utc = dt.datetime.utcnow()
        influence_processing_start = utc.replace(
            hour=dt.datetime.strptime(config['General']['inf_tick_start'], '%H:%M').hour,
            minute=dt.datetime.strptime(config['General']['inf_tick_start'], '%H:%M').minute,
            second=0)
        influence_processing_end = utc.replace(
            hour=dt.datetime.strptime(config['General']['inf_tick_end'], '%H:%M').hour,
            minute=dt.datetime.strptime(config['General']['inf_tick_start'], '%H:%M').minute,
            second=0)

        if utc > influence_processing_end:  # Influence has already been processed today, calc time until tomorrow
            try:
                influence_processing_start = influence_processing_start.replace(day=influence_processing_start.day + 1)
            except ValueError:
                influence_processing_start = influence_processing_start.replace(
                    day=1,
                    month=influence_processing_start.month + 1
                )
        delta = influence_processing_start - utc

        if utc < influence_processing_start:  # Influence window has yet to occur
            remaining_hours = delta.seconds / 3600
            if remaining_hours >= 1.2:
                countdown = 'Influence tick begins in around {} hours.'.format(str(remaining_hours)[0:2])
            elif remaining_hours < 1.2 and remaining_hours > 1:
                countdown = 'Influence tick begins in around an hour.'
            elif remaining_hours < 1 and remaining_hours > 0.5:
                countdown = 'Influence tick begins in less than an hour.'
            elif remaining_hours < 0.15:
                countdown = 'Influence tick begins shortly.'
        elif utc > influence_processing_start and utc < influence_processing_end:  # Influence is calculating now
            countdown = 'Influence is currently being calculated.'

    except Exception as e:
        log.exception('Encountered exception determine influence tick.', e)
        pass
    else:
        tick_countdown.config(text=countdown)
        tick_countdown.after(1000, lambda c=config: tick_server(c))



'''###########################################
#           misc. window/menu functions
###########################################'''


# close gracefully
def graceful_close(root, monitor_data, monitor_status, monitor_journal, eddn_dispatcher):
        log.info('Stopping all threads.')
        if monitor_status.isAlive():
            monitor_status.stop()
            monitor_status.join()
        if monitor_journal.isAlive():
            runtime['journal_byte_offset'] = monitor_journal.update_offset()
            monitor_journal.join()
        if eddn_dispatcher.isAlive():
            eddn_dispatcher.stop()
            eddn_dispatcher.join()
        monitor_data.save_session(runtime)
        if not monitor_journal.isAlive():
            monitor_data.join()
        log.info('Shutting down.')
        root.destroy()


#FIXME this is just awful
def advisor_state_flavour_text():
    if runtime['target_faction_state'] or runtime['advisor_init'] == False:
        #print('a' + runtime['target_faction_state'])
        #print(runtime['old_target_faction_state'])
        runtime['old_target_faction_state'] = runtime['target_faction_state']
        runtime['advisor_init'] = True
        data = advisor(runtime)
        #print(data)
        return data
    else:
        data = 'I\'ve got nothing.'
        return data



'''###########################################
#             thread config
###########################################'''

def start_threads(monitor_data, monitor_status, monitor_journal, eddn_dispatcher):
    try:
        log.info('Starting threads and configuring session.')
        monitor_data.start()
        monitor_data.configure_session(runtime)
        monitor_status.start()
        monitor_journal.start()
        if eval(config['Options']['eddn_enabled']):
            eddn_dispatcher.start()
    except Exception as e:
        log.exception('Exception occured ensuring threads were alive.', e)


# Get message string from message queue
class MessageMonitor(threading.Thread):
    def __init__(self, status_queue):
        log.info('Initalising MessageMonitor') ##DEBUG
        super(MessageMonitor, self).__init__()
        self._stop_event = threading.Event()
        self.msgqueue = status_queue

    def run(self):
        self.monitor_messages()

    def ts(self): #return timestamp
        self.time = dt.datetime.strftime(dt.datetime.utcnow(), '%H:%M:%S - ')

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def monitor_messages(self):
        while not self.stopped():
            try:
                self.ts()
                msg = self.msgqueue.get(block = False)
                msg = self.time + msg
                status_line.set(msg)
            except queue.Empty:
                pass
            except Exception as e:
                log.exception('MessageMonitor hit exception reading queue.', e)
                pass
            sleep(0.1)


# Data queue monitor
class DataBroker(threading.Thread):
    def __init__(self, message_queue, data_queue):
        log.info('Initialsing DataBroker')
        super(DataBroker, self).__init__()
        self._stop_event = threading.Event()
        self.datqueue = data_queue
        self.msgqueue = message_queue
        # establish database agent
        self.sql = db.DatabaseAgent()

    def run(self):
        self.monitor_data()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def monitor_data(self):
        while not self.stopped():
            try:
                if not self.datqueue.empty():
                    data = self.datqueue.get(block = False)
                    log.debug('DataBroker received: ' + str(data))
                    # handle missions
                    if 'mission' in data.keys():
                        if 'status' in data['mission'].keys():
                            if data['mission']['status'] == 'completed':
                                try:
                                    data['mission']['mission_giver_system'], data['mission']['mission_giver_station'], data['mission']['mission_giver_faction'] = self.sql.lookup_mission(data['mission']['mission_id'])
                                    voucher_tracker(data, self.msgqueue)
                                    log.debug('DataBroker dispatching mission update to DB.')
                                    self.sql.update_mission_status(data)
                                except TypeError: #will throw this if the mission has already been processed
                                    log.debug('received no data from lookup.')
                                    pass
                            else:
                                log.debug('DataBroker dispatching new mission to DB.')
                                voucher_tracker(data, self.msgqueue)
                                self.sql.insert_mission(data, runtime)
                    # handle vouchers
                    if 'voucher' in data.keys():
                        log.debug('DataBroker dispatching voucher data to DB.')
                        voucher_tracker(data, self.msgqueue)
                        if 'valid' in data['voucher'].keys():
                            if data['voucher']['valid'] != 'invalid':
                                log.debug('DataBroker calling DB update.')
                                self.sql.insert_voucher(data, runtime)
            except Exception as e:
                log.exception('Databroker exception while monitoring queue.', e)
                pass

            sleep(0.1)

    def bgs_report(self, runtime):
        data = self.sql.get_bgs(runtime)
        return data

    #expects a list
    def remove_bgs(self, id_list):
        self.sql.mark_processed(id_list)

    def save_session(self, runtime):
        self.sql.save_session_data(runtime)
        self.stop()

    def retrieve_session(self):
        return self.sql.lookup_session_data()

    def configure_session(self, runtime):
        old_session = self.retrieve_session()
        if old_session:
            self.push_msg('Found old session data.')
            log.info('Updating runtime with previous session data.')
            log.debug('Previous session data: ' + str(old_session))
            log.debug('Runtime before session update: ' + str(runtime))
            runtime.update(old_session[0])
            # because sqllite doesn't do booleans this has to exist
            if old_session[0]['docked'] == 'True':
                runtime['docked'] = True
            else:
                runtime['docked'] = False
            if old_session[0]['landed'] == 'True':
                runtime['landed'] = True
            else:
                runtime['landed'] = False
            if old_session[0]['in_srv'] == 'True':
                runtime['in_srv'] = True
            else:
                runtime['in_srv'] = False
            if old_session[0]['system_is_target_faction_owned'] == 'True':
                runtime['system_is_target_faction_owned'] = True
            else:
                runtime['system_is_target_faction_owned'] = False
            log.debug('Runtime after session update: ' + str(runtime))
            runtime['stats_set'] = True
        else:
            log.info('No previous session data found.')

    def push_msg(self, msg):
        log.debug('Databroker pushing message queue\n'+ str(msg))
        self.msgqueue.put(msg)

# Journal handler
class JournalMonitor(threading.Thread):
    def __init__(self, status_queue, data_queue):
        log.info('Initialsing JournalMonitor')
        super(JournalMonitor, self).__init__()
        self._stop_event = threading.Event()
        self.msgqueue = status_queue
        self.datqueue = data_queue
        self.journal_path = runtime['journal_path']

    def run(self):
        self.monitor_journal()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def update_offset(self):
        self.stop()
        return self.journal_file.tell()


    def monitor_journal(self):
        while not self.stopped():
            self.newfile = False
            try:
                newest = max(glob.iglob(path.join(runtime['journal_path'], '*.log')), key=path.getctime)

                if runtime['journal_file'] != newest:
                    runtime['journal_file'] = newest
                    self.msgqueue.put('New journal detected. Opening file.')
                    sanitized_name = newest.split('\\')[-1]
                    log.info('JournalMonitor found new file: ' + sanitized_name)
                    self.journal_file = open(newest, 'r')
                    log.debug('JournalMonitor resetting offset value.')
                    self.journal_byte_offset = 0
                    self.newfile = True
                elif self.newfile == False:
                    if not hasattr(self, 'journal_byte_offset'):
                        self.journal_byte_offset = runtime['journal_byte_offset']
                        log.debug('JournalMonitor using offset ' + str(self.journal_byte_offset)) ##DEBUG
                    if not hasattr(self, 'journal_file'):
                        log.info('JournalMonitor opening old journal.')
                        self.journal_file = open(newest, 'r')
                        log.debug('JournalMonitor moving to previous offset.')
                        self.journal_file.seek(self.journal_byte_offset)
            except ValueError:
                msg = 'Could not find journal files at "{}".'.format(runtime['journal_path'])
                log.error(msg)
                self.msgqueue.put(msg)
            except Exception as e:
                log.exception('JournalMonitor hit exception checking for file.', e)

            try:
                file_data = self.journal_file.readline()
                self.journal_byte_offset = self.journal_file.tell()
                self.parse(file_data)
                sleep(0.05)
            except Exception as e:
                log.exception('Exception occured parsing JSON.', e)



    def parse(self, file_data):
        if file_data:
            data = json.loads(file_data)
            log.debug('JournalMonitor parsing JSON')
            #log.debug(data)

            event = data['event']
            update = defaultdict(dict)


            # ----- Misc. Statistical related stuff -----

            if event == 'LoadGame':
                log.debug('JournalMonitor found ' + event + '.')
                if not runtime['stats_set']:
                    self.push_msg('Loaded statistics.')
                    log.info('Loaded statistics.')
                    update['stats_set'] = True
                update['commander_name'] = data['Commander']
                update['ship_name'] = data['ShipName']
                update['ship'] = data['Ship']  #FerDeLance, etc
                update['game_mode'] = data['GameMode'] #Group/Open/Solo

                # Capture which private group you're in
                if update['game_mode'] == 'Group':
                    update['game_mode_group'] = data['Group']
                else:
                    update['game_mode_group'] = ''
                update['target_faction_state'] = ''
                update['old_target_faction_state'] = ''
                update['advisor_init'] = False
                # credits start is always reset in a new session
                log.debug('JournalMonitor setting initial credit value')
                update['credits'] = data['Credits']

            elif event == 'Loadout':
                log.debug('JournalMonitor found ' + event + '.')
                update['ship_name'] = data['ShipName']
                update['ship'] = data['Ship']

            elif event == 'RefuelAll' or event == 'RefuelPartial':
                log.debug('JournalMonitor found ' + event + '.')
                update['low_fuel'] = False

            elif event == 'UserShipName':
                log.debug('JournalMonitor found ' + event + '.')
                update['ship_name'] = data['UserShipName']
                update['ship'] = data['Ship']

            # ----- Location related stuff -----

            elif event == 'Location':
                log.debug('JournalMonitor found ' + event + '.')
                if not runtime['name_set']:
                    self.push_msg('Initialised. Waiting for events...')
                update['star_system'] = data['StarSystem']
                if 'SystemFaction' in data.keys():
                    update['system_owner'] = data['SystemFaction']
                    if data['SystemFaction'] == runtime['target_faction']:
                        update['system_is_target_faction_owned'] = True
                    update['system_owner'] = data['SystemFaction']
                else:
                    update['system_is_target_faction_owned'] = False

                if data['Population'] > 0:
                    update['system_pop'] = '{:,}'.format(data['Population'])
                else:
                    update['system_pop'] = 'Nobody lives here.'
                update['target_faction_state'] = self.state_finder(data)
                update['near_body'] = None
                update['near_body_type'] = None
                update['docked'] = data['Docked'] #True / False
                update['location_data_present'] = True

                if update['docked'] == True:
                    update['station_name'] = data['StationName']

            elif event == 'StartJump':
                log.debug('JournalMonitor found ' + event + '.')
                update['jump_type'] = data['JumpType'] #Supercruise/Hyperspace
                try:
                    if data['Body']:
                        log.debug('JournalMonitor found near body:' + data['Body'] + '.')
                        update['near_body'] = data['Body']
                except:
                    pass
                try:
                    if update['jump_type'] == 'Supercruise':
                        log.debug('JournalMonitor cleared near_body, station_name.')
                        update['near_body'] = ''
                        update['near_body_type'] = ''
                        update['station_name'] = ''
                        update['station_faction'] = ''
                        update['supercruise'] = True
                except:
                    update['supercruise'] = True
                    pass

            elif event == 'SupercruiseEntry':
                log.debug('JournalMonitor found ' + event + '.')
                update['supercruise'] = True

            elif event == 'SupercruiseExit':
                log.debug('JournalMonitor found ' + event + '.')
                update['star_system'] = data['StarSystem']
                update['near_body'] = data['Body']  #"Col 285 Sector RE-P c6-5 A 6 a"
                update['jump_type'] = ''
                update['supercruise'] = False
                if 'near_body_type' in data.keys():
                    if data['near_body_type'] == 'Star':
                        update['station_name'] = ''
                    elif data['near_body_type'] == 'Station':
                        update['near_body_type'] = data['BodyType']
                        update['station_name'] = update['Body']
                    elif data['near_body_type'] == 'Null':
                        update['near_body_type'] == ''

            elif event == 'FSDJump':
                log.debug('JournalMonitor found ' + event + '.')
                update['star_system'] = data['StarSystem']
                update['target_faction_state'] = self.state_finder(data)
                update['system_pop'] = data['Population']
                update['fuel']  = data['FuelLevel']  # "FuelLevel":12.872868 #REVIEW need to find how this is actually expressed (tonnes/percentage)
                if 'Body' in data.keys():  #REVIEW may not be needed
                        log.debug('JournalMonitor found near body:' + data['Body'] + '.')
                        update['near_body'] = data['Body']
                else:
                    log.debug('JournalMonitor cleared near_body, near_body_type, station_name.')
                    update['near_body'] = ''
                    update['near_body_type'] = ''
                    update['station_name'] = ''
                    pass
                update['supercruise'] = True

            elif event == 'Docked':
                log.debug('JournalMonitor found ' + event + '.')
                update['station_name'] = data['StationName']
                update['station_faction'] = data['StationFaction']
                update['']
                if 'FactionState' in data.keys():     # Workshops don't have faction states
                    update['station_faction_state'] = data['FactionState']
                    if update['station_faction_state'] == 'None':
                        update['station_faction_state'] = 'N/A'
                update['star_system'] = data['StarSystem']
                update['docked'] = True
                if update['station_faction'] == runtime['target_faction']:  #REVIEW questionable value
                    if 'FactionState' in data.keys():
                        log.debug('Found {} in state: {}'.format(runtime['target_faction'], data['FactionState']))
                        update['target_faction_state'] = data['FactionState']

            elif event == 'Undocked':
                log.debug('JournalMonitor found ' + event + '.')
                update['station_faction'] = ''
                log.debug('JournalMonitor cleared station_faction.')
                update['docked'] = False


            # ----- SRV/Plantary related stuff -----

            elif event == 'ApproachBody':  # Going orbital
                log.debug('JournalMonitor found ' + event + '.')
                update['orbital'] = True
                update['near_body'] = data['Body']  # Eranin 2

            elif event == 'LeaveBody':  # Leaving orbital
                log.debug('JournalMonitor found ' + event + '.')
                update['orbital'] = False
                update['near_body'] = ''

            elif event == 'ApproachSettlement':
                log.debug('JournalMonitor found ' + event + '.')
                update['station_name'] = data['Name']  # Palmer Exchange ++

            elif event == 'LaunchSRV':
                log.debug('JournalMonitor found ' + event + '.')
                update['in_srv'] = True

            elif event == 'DockSRV':
                log.debug('JournalMonitor found ' + event + '.')
                update['in_srv'] = False

            elif event == 'SRVDestroyed':
                log.debug('JournalMonitor found ' + event + '.')
                update['in_srv'] = False
                update['in_ship'] = True

            elif event == 'Touchdown':
                log.debug('JournalMonitor found ' + event + '.')
                update['landed'] = True

            elif event == 'Liftoff':
                log.debug('JournalMonitor found ' + event + '.')
                update['landed'] = False


            # ----- BGS related stuff -----

            elif event == 'RedeemVoucher':
                log.debug('JournalMonitor found ' + event + '.')
                update['voucher']['timestamp'] = data['timestamp']
                update['voucher']['type'] = data['Type']   # scannable / bounty / CombatBond
                update['voucher']['factions'] = [] # make list
                faction_no =0
                if 'Factions' in data.keys():
                    for f in data['Factions']:
                        log.debug('Found faction: ' + str(f))
                        if f['Faction'] not in ['Federation', 'Alliance', 'Empire']:
                            if len(f['Faction']) == 0:
                                update['voucher']['factions'].append([runtime['station_faction'], f['Amount']])
                            else:
                                update['voucher']['factions'].append([f['Faction'],f['Amount']])
                                faction_no +=1
                elif 'Faction' in data.keys():
                    update['voucher']['factions'].append([data['Faction'], data['Amount']])
                else:
                    update['voucher']['factions'].append([runtime['station_faction'], data['Amount']])
                update['voucher']['valid'] = self.valid_voucher(update['voucher'])

            # filter missions out from donations
            elif event == 'MissionAccepted':
                log.debug('JournalMonitor found ' + event + '.')
                if data['Name'] == 'Mission_AltruismCredits':
                    update['mission']['type'] = 'donation'
                    log.debug('JournalMonitor found type - ' + update['mission']['type'] + ' mission.')
                else:
                    update['mission']['type'] = 'mission'
                    log.debug('JournalMonitor found type - ' + update['mission']['type'] + '.')
                update['mission']['status'] = 'accepted'
                update['mission']['mission_id'] = data['MissionID']
                update['mission']['station_name'] = runtime['station_name']
                update['mission']['influence'] = data['Influence']
                update['mission']['faction'] = data['Faction']
                update['mission']['influence'] = data['Influence']

            elif event == 'MissionCompleted':
                log.debug('JournalMonitor found ' + event + '.')
                if data['Name'] == 'Mission_AltruismCredits_name':
                    update['mission']['type'] = 'donation'
                    log.debug('JournalMonitor found completing ' + update['mission']['type'] + ' mission.')
                else:
                    update['mission']['type'] = 'mission'
                    log.debug('JournalMonitor found completing ' + update['mission']['type'] + '.')
                update['mission']['mission_id'] = data['MissionID']

                if 'Reward' in data.keys():
                    update['mission']['amount'] = data['Reward']
                elif 'Donation' in data.keys():                         ## REVIEW FIXME Due to 3.0, mission rewards are
                    update['mission']['amount'] = data['Donation']      # handled differently and may need to be rewritten
                update['mission']['status'] = 'completed'
                update['mission']['valid'] = self.valid_voucher(update['mission'])

            elif event == 'SellExplorationData':
                log.debug('JournalMonitor found ' + event + '.')
                update['voucher']['timestamp'] = data['timestamp']
                update['voucher']['type'] = 'exploration'
                update['voucher']['amount'] = data['BaseValue'] + data['Bonus']
                update['voucher']['valid'] = self.valid_voucher(update['voucher'])

            elif event == 'MarketSell':
                log.debug('JournalMonitor found ' + event + '.')
                update['voucher']['timestamp'] = data['timestamp']
                update['voucher']['amount'], update['voucher']['profit_made'] = self.determine_trade_profit(data['Count'], data['SellPrice'], data['AvgPricePaid'])
                #update['voucher']['commodity'] = data['Type']
                traded = data['Type']
                tonnes = data['Count']  #FIXME do something with tonnage

                if 'BlackMarket' in data.keys(): #True/False
                        log.debug('JournalMonitor found black market trade.')
                        update['voucher']['type'] = 'smuggled'
                        update['voucher']['valid'] = self.valid_voucher(update['voucher'])
                else:
                    log.debug('JournalMonitor found legitimate market trade.')
                    update['voucher']['type'] = 'trade'
                    update['voucher']['valid'] = self.valid_voucher(update['voucher'])
                    pass
                # Since we've now tested validity of the commodity against the state
                # we can stomp the commodity traded into it's category
                if traded in commodities.group['foods']:
                    update['voucher']['commodity'] = 'Food'
                elif traded in commodities.group['weapons']:
                    update['voucher']['commodity'] = 'Weapons'
                elif traded in commodities.group['medicines']:
                    update['voucher']['commodity'] = 'Medicines'
                else:
                    update['voucher']['commodity'] = 'Misc'

            # send the data
            if len(update) >0:
                log.debug('Parsed useful data: '+ str(data))
                if 'voucher' in update.keys() or 'mission' in update.keys():
                    self.push_data(update)
                if 'voucher' not in update.keys() and 'mission' not in update.keys():
                    runtime.update(update)
                    location_parse()
                    log.debug('Runtime after update: \n'+ str(runtime))
            else:
                log.debug('JournalMonitor received useless data. ({})'.format(event))



    # find state of target faction in system, called on FSDJump/Location
    def state_finder(self, event):
        runtime['old_target_faction_state'] = runtime['target_faction_state']
        if runtime['target_faction_state']:
            log.debug('Clearing {}\'s faction state for refresh.'.format(runtime['target_faction']))
            runtime['target_faction_state'] = ''
        if 'Factions' in event.keys():
            log.debug('Found faction data')
            for faction in event['Factions']:
                if faction['Name'] == runtime['target_faction']:
                    if 'FactionState' in faction.keys():
                        a = faction['FactionState']
                        log.debug('Found {} in state: {}'.format(runtime['target_faction'], faction['FactionState']))
                        return a
        if 'a' not in locals():
            log.debug('Failed to find {} in faction data'.format(runtime['target_faction']))
            return None



    # determine validity of voucher and it's effect on the system state
    def valid_voucher(self, event, *commodity):
        will_effect_influence = ''
        will_decrease_duration = ''
        will_increase_duration = ''
        log.info('Determining validity of this voucher.')

        state = runtime['target_faction_state'] # REVIEW not quite satisified with this...
        log.debug(state)
        log.debug(event['type'])
        log.debug(str(event))

        if event['type'] == 'bounty' or event['type'] == 'CombatBond':
            if state in ['Elections', 'Famine', 'Outbreak']: #REVIEW confirm Elections type
                reason = 'Redeemed Combat Bond for faction in state: {}'.format(state)
                will_effect_influence = False
            elif state in ['Lockdown', 'CivilUnrest']:    #REVIEW confirm CivilUnrest type
                will_decrease_duration = True
            else:
                will_effect_influence = True

        if event['type'] == 'mission' or event['type'] == 'donation':   #REVIEW FIXME combat missions count here
            if state in ['War', 'Civil War', 'Famine', 'Outbreak', 'Lockdown']:
                reason = 'Mission completed for faction in state: {}'.format(state)
                will_effect_influence = False
            #elif event['influence'] == 'None':
        #        reason = 'Mission completed with no influence reward.'      ## REVIEW FIXME Due to 3.0, mission rewards are
        #        will_effect_influence = False                               # handled differently and may need to be rewritten
            else:
                will_effect_influence = True

        if event['type'] == 'exploration' or event['type'] == 'scannable':
            if state in ['Boom', 'Expansion', 'Investment']:
                will_increase_duration = True
            elif state in ['Bust', 'Famine', 'Outbreak']:
                will_decrease_duration = True
            elif state in ['War', 'CivilWar']:
                reason = 'Redeemed exploration data for faction in state: {}'.format(state)
                will_effect_influence = False
            else:
                will_effect_influence = True

        if event['type'] == 'trade':
            print(commodities.group['weapons'])
            if event['profit_made'] == True:
                if state in ['Boom']:
                    will_increase_duration = True
                elif state in ['Bust']:
                    will_decrease_duration = True
                elif state in ['CivilUnrest']:   #REVIEW confirm CivilUnrest type
                    if commodity in commodity_group['weapons']:
                        will_increase_duration = True
                elif state in ['Famine']:
                    if commodity in commodity_group['foods']:
                        will_decrease_duration = True
                elif state in ['Outbreak']:
                    if commodity in commodity_group['medicines']:
                        will_decrease_duration = True
                elif state in ['War', 'CivilWar', 'Lockdown']:
                    reason = 'Conducted normal trade for faction in state: {}'.format(state)
                    will_effect_influence = False
                else:
                    will_effect_influence = True
            # else:
            #     reason = 'Failed to make a profit'
            #     will_effect_influence = False

        if event['type'] == 'smuggled':
            if event['profit_made'] == True:
                if state in ['CivilUnrest']:
                    if commodity in commodities.group['weapons']:
                        will_increase_duration = True
                elif state in ['Famine']:
                    if commodity in commodities.group['foods']:
                        will_decrease_duration = True
                elif state in ['Outbreak']:
                    if commodity in commodities.group['medicines']:
                        will_decrease_duration = True
                elif state in ['Lockdown', 'CivilUnrest']: #REVIEW confirm CivilUnrest type
                    will_increase_duration = True
                else:
                    will_effect_influence = True
            # else:
            #     reason = 'Failed to make a profit'
            #     will_effect_influence = False

        if will_increase_duration:
            log.info('Determined this voucher will extend current state.')
            result = 'increase'
        elif will_decrease_duration:
            log.info('Determined this voucher will reduce current state.')
            result = 'decrease'
        elif not will_effect_influence:
            log.info('Determined this voucher is invalid (will not effect influence).')
            if 'reason' in locals(): ##FIXME should always have a reason..
                log.info('Reason: {}'.format(reason))
            else:
                log.error('Voucher {} did not specify a reason as to why it does not affect influence!'.format(str(event)))
            result = 'invalid'
        else:
            log.info('Determined this voucher is valid.')
            result = 'valid'
        return result


    def determine_trade_profit(self, count, sell_price, buy_price):
        try:
            log.debug('Determining whether a profit was made.')
            delta = sell_price - buy_price
            total = delta * count
            if total >0:
                log.info('Profit of ' + str(total) + ' made.')
                profit_made = True
            else:
                log.info('Lost ' + str(total) + ' on this trade.')
                profit_made = False
            return total, profit_made
        except Exception as e:
            log.exception('Exception occured determining trade profit:', e)


    def push_msg(self, msg):
        log.debug('JournalMonitor pushing message queue\n'+ str(msg))
        self.msgqueue.put(msg)

    def push_data(self, msg):
        log.debug('JournalMonitor pushing data queue:\n'+ str(msg))
        self.datqueue.put(msg)

if __name__ == '__main__':
    main()
