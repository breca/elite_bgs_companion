from . import bucket
from tkinter import *
from tkinter import ttk

# bug report window
def window_report_bug(root):
    win = Toplevel(root)
    win.geometry("+%d+%d" % (root.winfo_rootx(), root.winfo_rooty()))
    win.iconbitmap(r'images\favicon.ico')
    win.title('RSC: Report a bug')
    bug_frame = ttk.Frame(win, padding="3 3 3 3")
    bug_frame.grid()

    bugtext = bucket.bugtext

    bug_lbl = Label(bug_frame, text=bugtext, padx=20, pady=0, anchor=W, justify=LEFT)#, font=('times', 20, 'bold'))
    bug_lbl.grid(row=0,column=0,sticky=W)

    bug_button = Button(bug_frame, padx=20, command=win.destroy, text='Fine...')
    bug_button.grid(row=1,column=0,sticky=S)
