from . import bucket
from tkinter import *
from tkinter import ttk
from . import log

# optits window
def window_options(root, config):
    win = Toplevel(root)
    win.geometry("+%d+%d" % (root.winfo_rootx(), root.winfo_rooty()))
    win.iconbitmap(r'images\favicon.ico')
    win.title('Options')
    opt_frame = ttk.Frame(win, padding="10 10 10 10")
    opt_frame.grid()

    # Initialise vars
    eddn = BooleanVar(win)
    updates_on_start = BooleanVar(win)

    # Update vars from settings.ini
    eddn.set(config['Options']['EDDN_Enabled'])
    updates_on_start.set(config['Options']['Check_Updates_On_Start'])

    opt1 = Label(opt_frame, text='Upload system/station/market data to the Elite Dangerous Data Network', padx=0, pady=0, anchor=W, justify=LEFT)
    opt1.grid(row=1,column=1,sticky=W)
    chk1 = Checkbutton(opt_frame, variable=eddn)
    chk1.grid(row=1, column=0)

    opt2 = Label(opt_frame, text='Automatically check for updates on startup', padx=0, pady=0, anchor=W, justify=LEFT)
    opt2.grid(row=2,column=1,sticky=W)
    chk2 = Checkbutton(opt_frame, variable=updates_on_start)
    chk2.grid(row=2, column=0)

    # Buttons
    opt_but_frame = ttk.Frame(win, padding="10 10 10 10")
    opt_but_frame.grid()

    opt_button1 = Button(opt_but_frame, padx=20, command=lambda a={
        'eddn': eddn,
        'updates': updates_on_start
        }: set_options(config, a, win), text='Change settings')
    opt_button1.grid(row=0,column=0, sticky=S)

    opt_button2 = Button(opt_but_frame, padx=20, command=win.destroy, text='Cancel')
    opt_button2.grid(row=0,column=2, sticky=S)


def set_options(config, a, window):
    log.info('Saving options...')
    log.debug(str(a))
    try:
        config.set('Options','EDDN_Enabled', str(a['eddn'].get()))
        config.set('Options','Check_Updates_On_Start', str(a['updates'].get()))
        with open('settings.ini', 'w') as f:
            config.write(f)
        window.destroy()
        log.info('Options saved.')
    except Exception as e:
        log.exception('Could not update settings.ini!', e)
        window.destroy()
        pass
