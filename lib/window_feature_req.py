from tkinter import *
from tkinter import ttk
from . import links

# feature request window
def window_feature_req(root):
    win = Toplevel(root)
    win.geometry("+%d+%d" % (root.winfo_rootx(), root.winfo_rooty()))
    win.iconbitmap(r'images\favicon.ico')
    win.title('Feature requests')
    req_frame = ttk.Frame(win, padding="20 20 20 20")
    req_frame.grid()

    req_lbl1 = Label(req_frame, text='Got a cool idea for something you\'d like to see this application do?', padx=20, anchor=N, justify=LEFT)#, font=('times', 20, 'bold'))
    req_lbl1.grid(row=0,column=0,sticky=N)

    req_lbl2 = Label(req_frame, text='           ', padx=20, anchor=N, justify=LEFT)#, font=('times', 20, 'bold'))
    req_lbl2.grid(row=1,column=0,sticky=N)

    for row in range(2,4):
        Grid.rowconfigure(req_frame, row, weight=1)

    tz_button = Button(req_frame, padx=20, pady=10, command=links.feature_request, text='Submit an issue with your idea/request to Github (preferred)')
    tz_button.grid(row=2,column=0,sticky=N+S+E+W)

    tz_button = Button(req_frame, padx=20, pady=10, command=links.discord, text='Hassle the developer on Radio Sidewinder\'s Discord')
    tz_button.grid(row=3,column=0,sticky=N+S+E+W)

    tz_button = Button(req_frame, padx=20, pady=10, command=win.destroy, text='Eh, nevermind.')
    tz_button.grid(row=4,column=0,sticky=N+S+E+W)
