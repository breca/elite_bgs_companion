from . import bucket
from tkinter import *
from tkinter import ttk

# feature request window
def window_feature_req(root):
    win = Toplevel(root)
    win.geometry("+%d+%d" % (root.winfo_rootx(), root.winfo_rooty()))
    win.iconbitmap(r'images\favicon.ico')
    win.title('RSC: Feature request')
    req_frame = ttk.Frame(win, padding="20 20 20 20")
    req_frame.grid()

    req_text = bucket.req_text

    req_lbl = Label(req_frame, text=req_text, padx=20, pady=0, anchor=W, justify=LEFT)#, font=('times', 20, 'bold'))
    req_lbl.grid(row=0,column=0,sticky=W)

    tz_button = Button(req_frame, padx=20, command=win.destroy, text='Okay then.')
    tz_button.grid(row=1,column=0,sticky=S)
