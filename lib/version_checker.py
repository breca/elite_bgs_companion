from requests_futures.sessions import FuturesSession
import webbrowser
from . import log
from tkinter import *
from tkinter import ttk




def fetch(config):
    log.info('Checking for latest version.')
    url = config['General']['VersionURL'] + 'rsc_version'
    session = FuturesSession()
    try:
        r = session.get(url, timeout=5)
        response = r.result()
    except Exception as e:
        log.exception('Unable to contact remote server.', e)
        response = 'Error'
        return response
    else:
        return response.json()




def check(msg_queue, config, *force):
    try:
        msg_queue.put('Checking for updates...')
        log.info('Checking for updates.')

        response = fetch(config)
        if response != 'Error':
            if config['General']['Version'] != response['version']: #found update
                if config['General']['IgnoredUpdate'] != response['version'] or force:
                    if force == True:
                        log.info('Forced update check result: Found new version: {}'.format(response['version']))
                    else:
                        log.info('Found new version: {}'.format(response['version']))
                    win(response, config)
                elif config['General']['IgnoredUpdate'] == response['version']:
                    log.info('Found update ({}) but user has elected to skip this one.'.format(response['version']))
            elif config['General']['Version'] == response['version'] and force:
                msg('Your version is up to date.', config['General']['Version'])
                log.info('Forced update check result: Version is up to date. (Local: {}, Remote: {})'.format(config['General']['Version'], response['version']))
            else:
                log.info('This version is up to date.')
    except Exception as e:
        if force:
            msg('Could not retrieve update information at this time.')
        log.exception('Error occured during update check.', e)
        pass




def msg(msgtxt, *version):
    m_win = Tk()
    m_win.title('RSC: Update check')
    m_win.iconbitmap(r'.\images\favicon.ico')
    m_frame = ttk.Frame(m_win, padding="10 10 10 10")
    m_frame.grid()

    m_title_lbl_1 = Label(m_frame, text=msgtxt, padx=3, pady=5)
    m_title_lbl_1.grid(row=0, column=0, columnspan=5, sticky=N+E+W)

    if msgtxt == 'Could not retrieve update information at this time.':
        ex_b = Button(m_frame, text='Hm.', borderwidth=1, padx=10, pady=5, command=m_win.destroy)
        ex_b.grid(row=2, column=0, columnspan=5, padx=3, pady=3, sticky=S)
    else:
        tx_2 = Label(m_frame, text='Your version:', padx=3, pady=5)
        tx_2.grid(row=1, column=1,sticky=E)
        tx_3 = Label(m_frame, text=version, padx=3, pady=5)
        tx_3.grid(row=1, column=2,sticky=W)
        tx_4 = Label(m_frame, text='Latest version:', padx=3, pady=5)
        tx_4.grid(row=1, column=3,sticky=E)
        tx_5 = Label(m_frame, text=version, padx=3, pady=5)
        tx_5.grid(row=1, column=4,sticky=W)
        ex_b = Button(m_frame, text='Sweet.', borderwidth=1, padx=10, pady=5, command=m_win.destroy)
        ex_b.grid(row=2, column=0, columnspan=5, padx=3, pady=3, sticky=S)




def skip_update(new_version, config, window):
    log.info('Ignoring this version ({}).'.format(new_version))
    try:
        config.set('General','IgnoredUpdate', new_version)
        with open('settings.ini', 'w') as f:
            config.write(f)
        window.destroy()
    except Exception as e:
        log.exception('Could not update settings.ini!', e)
        window.destroy()



def win(response, config):
    version = config['General']['Version']
    url = config['General']['VersionURL']
    url = url + 'RSC Companion.zip'
    v_win = Tk()
    v_win.title('RSC: Update available!')
    v_win.iconbitmap(r'.\images\favicon.ico')

    v_frame = ttk.Frame(v_win, padding="10 10 10 10")
    v_frame.grid()
    v_frame.columnconfigure(1, weight=1)
    v_frame.columnconfigure(3, weight=1)

    v_title_lbl_1 = Label(v_frame, text='Update Available!', padx=3, pady=5)
    v_title_lbl_1.grid(row=0, column=0, columnspan=5, sticky=N+E+W)

    tx_1 = Label(v_frame, text='Your version:', padx=3, pady=5)
    tx_1.grid(row=1, column=1, columnspan=1,sticky=E)
    tx_2 = Label(v_frame, text=version, padx=3, pady=5)
    tx_2.grid(row=1, column=2, columnspan=1,sticky=W)
    tx_1 = Label(v_frame, text='New version:', padx=3, pady=5)
    tx_1.grid(row=1, column=3,columnspan=1,sticky=E)
    tx_2 = Label(v_frame, text=response['version'], padx=3, pady=5)
    tx_2.grid(row=1, column=4, columnspan=1,sticky=W)

    v_title_lbl_2 = Label(v_frame, text='Changelog:', padx=3, pady=5)
    v_title_lbl_2.grid(row=2, column=0, columnspan=6, sticky=N+E+W)

    row = 3
    for line in response['changelog']:
        cl = Label(v_frame, text=line, padx=3, pady=3, wraplength=400, justify=LEFT)
        cl.grid(row=row, column=0, columnspan=5, sticky=W)
        row += 1

    mt_lbl = Label(v_frame, text="        ", padx=3, pady=3)
    mt_lbl.grid(row=row, column=0, columnspan=4, sticky=W)

    g_btn = Button(v_frame, text='Grab it!', borderwidth=1, padx=10, pady=5, command=lambda: webbrowser.open_new(url))
    g_btn.grid(row=row+1, column=0, columnspan=1, padx=3, pady=3, sticky=S)
    x_btn = Button(v_frame, text='Skip this update', borderwidth=1, padx=10, pady=5, command=lambda: skip_update(response['version'], config, v_win))
    x_btn.grid(row=row+1, column=1, columnspan=3, padx=3, pady=3, sticky=S)
    x_btn = Button(v_frame, text='Not right now', borderwidth=1, padx=10, pady=5, command=v_win.destroy)
    x_btn.grid(row=row+1, column=4, columnspan=1, padx=3, pady=3, sticky=S)
