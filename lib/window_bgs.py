from . import log
from tkinter import *
from tkinter import ttk
from collections import defaultdict
import datetime as dt
import copy

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

# bgs report window
def window_bgs(databroker, runtime):
    log.info('Opening BGS Stat window.')
    bgs_win = Tk()
    bgs_win.title('BGS Stats')
    bgs_win.iconbitmap(r'images\favicon.ico')

    # Create a canvas, then a frame embedded into the canvas. Attach a scrollbar to the canvas
    # qv https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter
    bgs_canvas = Canvas(bgs_win, width=600)

    bgs_vsb = Scrollbar( bgs_win, orient="vertical", command=bgs_canvas.yview)
    bgs_canvas.configure(yscrollcommand=bgs_vsb.set)

    bgs_vsb.pack(side="right",fill="y")
    bgs_canvas.pack(side="left", fill="both", expand=True)

    bgs_frame = ttk.Frame(bgs_canvas, padding="10 10 10 10")
    bgs_frame.grid()

    bgs_canvas.create_window((4,4), window=bgs_frame, anchor="nw")
    bgs_frame.bind("<Configure>", lambda event, canvas=bgs_canvas: onFrameConfigure(bgs_canvas))
    
    def bgs_empty(ids, databroker):
        log.debug('Attempting to empty BGS data.')
        databroker.remove_bgs(ids)

    bgs_win.rowconfigure(0, weight=2)
    for i in range(0,10):
        bgs_win.columnconfigure(i, weight=1)

    # get voucher and mission data
    report_dict = databroker.bgs_report(runtime)

    if report_dict:
        time = dt.datetime.strftime(dt.datetime.now(), '%H:%M')
        title_text = 'BGS report data as of {}. Click an entry to copy it to clipboard, ready for Discord.'.format(time)
        title_lbl_1 = Label(bgs_frame, text=title_text, padx=3, pady=5)
        title_lbl_1.grid(row=0, column=0, columnspan=9, sticky=N+E+W)

        rows=1

        # container for stoping our derived text from the below loop, for copying amounts to clipboard
        all_ids = []

        # REVIEW might not be needed since generation has moved to sql
        display_dict = {}
        display_dict = copy.deepcopy(dict(report_dict))

        for system in display_dict.keys():
            for station in display_dict[system]:
                for faction in display_dict[system][station]:
                    log.debug('Processing faction: ' + faction)
                    fact_lbl = Label(bgs_frame, text=faction, padx=3, pady=3, borderwidth=1, relief='ridge', anchor=W, font = "Verdana 10 bold")
                    fact_lbl.grid(row=rows, column=0, columnspan=9, padx=3, pady=3, sticky=E+W)
                    rows+=1
                    title_lbl_1 = Label(bgs_frame, text='System', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_1.grid(row=rows, column=0, sticky=NSEW)
                    title_lbl_2 = Label(bgs_frame, text='Station', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_2.grid(row=rows, column=1, sticky=NSEW)
                    title_lbl_2 = Label(bgs_frame, text='Bounties', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_2.grid(row=rows, column=2, sticky=NSEW)
                    title_lbl_3 = Label(bgs_frame, text='Combat\nBonds', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_3.grid(row=rows, column=3, sticky=NSEW)
                    title_lbl_3 = Label(bgs_frame, text='Donations', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_3.grid(row=rows, column=4, sticky=NSEW)
                    title_lbl_4 = Label(bgs_frame, text='Missions', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_4.grid(row=rows, column=5, sticky=NSEW)
                    title_lbl_5 = Label(bgs_frame, text='Trade', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_5.grid(row=rows, column=6, sticky=NSEW)
                    title_lbl_6 = Label(bgs_frame, text='Smuggling', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_6.grid(row=rows, column=7, sticky=NSEW)
                    title_lbl_7 = Label(bgs_frame, text='Exploration', borderwidth=1, relief='raised', padx=3, pady=3)
                    title_lbl_7.grid(row=rows, column=8, sticky=NSEW)
                    rows+=1
                    for transaction in display_dict[system][station][faction]:
                        #print('entering')
                        bounty = 0
                        combat = 0
                        donation = 0
                        trade = 0
                        mission = 0
                        smuggling = 0
                        exploration = 0
                        commodities = ''
                        try:
                            r_bounty = display_dict[system][station][faction][transaction]['bounty'][0]
                            bounty = '{:,}'.format(r_bounty)
                            bounty_ids = display_dict[system][station][faction][transaction]['bounty'][-1]
                            for f in bounty_ids:
                                all_ids.append(f)
                        except KeyError:
                            r_bounty = 0
                            bounty_ids = False
                            pass
                        try:
                            r_combat = display_dict[system][station][faction][transaction]['CombatBond'][0]
                            combat = '{:,}'.format(r_combat)
                            combat_ids = display_dict[system][station][faction][transaction]['CombatBond'][-1]
                            for f in combat_ids:
                                all_ids.append(f)
                        except KeyError:
                            r_combat = 0
                            combat_ids = False
                            pass
                        try:
                            if 'donation' in display_dict[system][station][faction][transaction]:
                                r_donation = display_dict[system][station][faction][transaction]['donation'][0]
                                donation = '{:,}'.format(r_donation)
                                donation_ids = display_dict[system][station][faction][transaction]['donation'][-1]
                                for f in donation_ids:
                                    all_ids.append(f)
                        except KeyError as e:
                            log.exception('Failed to add donations to window', e)
                            donation = 0
                            donation_ids = False
                            pass
                        try:
                            if 'trade' in display_dict[system][station][faction][transaction]:
                                r_trade = display_dict[system][station][faction][transaction]['trade'][0]
                                trade = '{:,}'.format(r_trade)
                                trade_ids = display_dict[system][station][faction][transaction]['trade'][-1]
                                for f in trade_ids:
                                    all_ids.append(f)
                                commodities = ', '.join(display_dict[system][station][faction][transaction]['trade'][1])
                        except KeyError as e:
                            log.exception('Failed to add trade to window', e)
                            trade = 0
                            commodities = ''
                            trade_ids = False
                            pass
                        try:
                            if 'mission' in display_dict[system][station][faction][transaction]:
                                r_mission = display_dict[system][station][faction][transaction]['mission'][0]
                                mission = '{:,}'.format(r_mission)
                                mission_ids = display_dict[system][station][faction][transaction]['mission'][-1]
                                for f in mission_ids:
                                    all_ids.append(f)
                        except KeyError:
                            mission = 0
                            mission_ids = False
                            pass
                        try:
                            if 'smuggled' in display_dict[system][station][faction][transaction]:
                                r_smuggling = display_dict[system][station][faction][transaction]['smuggled'][0]
                                smuggling = '{:,}'.format(r_smuggling)
                                smuggling_ids = display_dict[system][station][faction][transaction]['smuggled'][-1]
                                for f in smuggling_ids:
                                    all_ids.append(f)
                                commodities = ', '.join(display_dict[system][station][faction][transaction]['smuggled'][1])
                        except KeyError:
                            smuggling = 0
                            commodities = ''
                            smuggling_ids = False
                            pass
                        try:
                            r_exploration = display_dict[system][station][faction][transaction]['exploration'][0]
                            exploration_ids = display_dict[system][station][faction][transaction]['exploration'][-1]
                            for f in exploration_ids:
                                all_ids.append(f)
                            exploration = '{:,}'.format(r_exploration)
                        except KeyError:
                            exploration_ids = False
                            exploration = 0
                            pass

                        report_line = '> {} > {} > {}'.format(faction, station, system)

                        sys = Label(bgs_frame, text=system, padx=3, pady=3)
                        sys.grid(row=rows, column=0, padx=3, pady=3)

                        stat = Label(bgs_frame, text=station, padx=3, pady=3)
                        stat.grid(row=rows, column=1, padx=3, pady=3)

                        but_bounty = '{} > Bounties {}'.format(bounty, report_line)
                        lbl1 = Button(bgs_frame, text=bounty, borderwidth=1, relief='sunken', padx=10, pady=3, command=lambda j=but_bounty: copy_to_clipboard(bgs_win, j))
                        lbl1.grid(row=rows, column=2, padx=3, pady=3, sticky=NSEW)

                        but_combat = '{} > Combat {}'.format(combat, report_line)
                        lbl2 = Button(bgs_frame, text=combat, borderwidth=1, relief='sunken', padx=10, pady=3, command=lambda j=but_combat: copy_to_clipboard(bgs_win, j))
                        lbl2.grid(row=rows, column=3, padx=3, pady=3, sticky=NSEW)

                        but_donate = '{} > Donations {}'.format(donation, report_line)
                        lbl3 = Button(bgs_frame, text=donation, borderwidth=1, relief='sunken', padx=10, pady=3, command=lambda j=but_donate: copy_to_clipboard(bgs_win, j))
                        lbl3.grid(row=rows, column=4, padx=3, pady=3, sticky=NSEW)

                        but_mission = '{} > Missions {}'.format(mission, report_line)
                        lbl4 = Button(bgs_frame, text=mission, borderwidth=1, relief='sunken', padx=10, pady=3, command=lambda j=but_mission: copy_to_clipboard(bgs_win, j))
                        lbl4.grid(row=rows, column=5, padx=3, pady=3, sticky=NSEW)

                        but_trade = '{} > Trade ({}) {}'.format(trade, commodities, report_line)
                        lbl3 = Button(bgs_frame, text=trade, borderwidth=1, relief='sunken', padx=10, pady=3, command=lambda j=but_trade: copy_to_clipboard(bgs_win, j))
                        lbl3.grid(row=rows, column=6, padx=3, pady=3, sticky=NSEW)

                        but_smuggling = '{} > Smuggling ({}) {}'.format(smuggling, commodities, report_line)
                        lbl4 = Button(bgs_frame, text=smuggling, borderwidth=1, relief='sunken', padx=10, pady=3, command=lambda j=but_smuggling: copy_to_clipboard(bgs_win, j))
                        lbl4.grid(row=rows, column=7, padx=3, pady=3, sticky=NSEW)

                        but_exploration = '{} > Exploration Data {}'.format(exploration, report_line)
                        lbl5 = Button(bgs_frame, text=exploration, borderwidth=1, relief='sunken', padx=10, pady=3, command=lambda j=but_exploration: copy_to_clipboard(bgs_win, j))
                        lbl5.grid(row=rows, column=8, padx=3, pady=3, sticky=NSEW)

                        rows+=1
            clr_btn = Button(bgs_frame, text='Clear All and Exit', borderwidth=1, padx=10, pady=5, command=lambda: [bgs_empty(all_ids, databroker),bgs_win.destroy()])
            clr_btn.grid(row=rows+1, column=0, columnspan=9, padx=3, pady=3, sticky=S)

            # Resize the main window to fit
            # Rows are ~32px high including padding
            # There's ~100px of fixed assets
            bch = min(rows * 32 + 100, 800)
            
            bgs_canvas.config(height=bch)
    else:
        lb = Label(bgs_frame, text='Nothing to report yet!', borderwidth=1, padx=10, pady=3)
        lb.grid(row=0, column=0, sticky=W, padx=3, pady=3)
        bgs_canvas.config(height=100)



# copy text from window into clipboard
def copy_to_clipboard(win, data):
    log.info('Copied data "{}" to clipboard.'.format(data))
    win.clipboard_clear()
    win.clipboard_append(data)
    win.update()
