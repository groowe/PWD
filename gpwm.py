#!/usr/bin/env python

# graphic passwordmanager.py

import tkinter as tk
from tkinter import ttk, Menu
import tkinter.font as font


def textinput(parrent,c):
    e = tk.Entry(parrent)
    e.grid(row=0,column=c)
    return e

if __name__ == '__main__':
    print('moo')
    win = tk.Tk()
    win.title = ('password manager')
    wf = tk.Frame(win,width = 300,height=200)
    wf.pack()
    textpack  = []
    for i in range(3):
        print(textpack)
        print(i)
        a = textinput(wf,i)

#        a.grid(row=0,column=i)

#        a.pack()
        textpack.append(a)
    print(textpack)
#    e.delete(0,END)
#    e.insert(0,'a default value')
#    s  = e.get()
    win.mainloop()
