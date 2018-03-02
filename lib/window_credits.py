from . import bucket
from tkinter import *
from tkinter import ttk

# credits window
def window_credits(root):
    win = Toplevel(root)
    win.geometry("+%d+%d" % (root.winfo_rootx(), root.winfo_rooty()))
    win.iconbitmap(r'images\favicon.ico')
    win.title('Credits')
    cred_frame = ttk.Frame(win, padding="3 3 3 3")
    cred_frame.grid()

    credtext = bucket.credtext

    cred_lbl = Label(cred_frame, text=credtext, padx=20, pady=0, anchor=W, justify=LEFT)#, font=('times', 20, 'bold'))
    cred_lbl.grid(row=0,column=0,sticky=W)

    cred_button = Button(cred_frame, padx=20, command=win.destroy, text='Aw.')
    cred_button.grid(row=1,column=0,sticky=S)
