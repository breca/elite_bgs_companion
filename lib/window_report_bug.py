from tkinter import *
from tkinter import ttk
from . import links

# bug report window
def window_report_bug(root):
    win = Toplevel(root)
    win.geometry("+%d+%d" % (root.winfo_rootx(), root.winfo_rooty()))
    win.iconbitmap(r'images\favicon.ico')
    win.title('Report a bug')
    bug_frame = ttk.Frame(win, padding="20 20 20 20")
    bug_frame.grid()

    bugtext1 = '''
This is a work in progress. The coder is lazy and terrible. Many mistakes were made. Oh god, the shame.

If you can, please do the following:

Step 1: Close Elite if it is still running.
Step 2: Process any BGS data that actually worked because we're going to delete your database.
Step 3: Close the companion.
Step 4: Edit the 'settings.ini' in your Companion directory and change the LogLevel to 'debug' (without quotes)
Step 5: Remove the 'companion.db' file under 'etc' in your Companion directory.
Step 6: Re-run the companion - it will play back over the journal file, hopefully reproducing the issue, creating a nice big fat log.

When it's done..

'''

    bugtext2 = '''

...and open an issue. Please include:

* Your OS, OS version (i.e Windows 10)
* Details of what happened / How to reproduce the bug

..attach the 'companion.log' file in your Companion directory to your report.

Don't forget to change the 'settings.ini' back to 'info' as debug mode can get pretty spammy. And weird things happen.

'''

    bug_lbl1 = Label(bug_frame, text=bugtext1, anchor=W, justify=LEFT)#, font=('times', 20, 'bold'))
    bug_lbl1.grid(row=0,column=0,sticky=W)

    bug_button = Button(bug_frame, padx=20, command=links.bug_report, text='...go to Github...')
    bug_button.grid(row=1,column=0,sticky=W)

    bug_lbl1 = Label(bug_frame, text=bugtext2, anchor=W, justify=LEFT)#, font=('times', 20, 'bold'))
    bug_lbl1.grid(row=2,column=0,sticky=W)

    bug_button = Button(bug_frame, padx=20, command=win.destroy, text='Fine...')
    bug_button.grid(row=3,column=0,sticky=S)
