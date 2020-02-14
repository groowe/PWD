import tkinter as tk
from tkinter import ttk
win = tk.Tk()
win.title('password manager')
fname = 'lg.gif'
bg = tk.PhotoImage(file=fname)
w = bg.width()
h = bg.height()

strs = "%dx%d+50+30" % (w,h)
win.geometry(strs)
cv = tk.Canvas(width=w,height=h)
cv.pack(side='top',fill='both',expand='yes')
cv.create_image(0,0,image=bg,anchor='nw')
win.mainloop()
