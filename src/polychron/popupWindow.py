import tkinter as tk
from tkinter import ttk


class popupWindow(object):
    def __init__(self, master):
        """initialises popupWindow"""
        self.top = tk.Toplevel(master)
        self.top.configure(bg="#AEC7D6")
        self.top.geometry("1000x400")
        # pop up window to allow us to enter a context that we want to change the meta data for
        self.l = ttk.Label(self.top, text="Context Number")
        self.l.pack()
        self.e = ttk.Entry(self.top)  # allows us to keep t6rack of the number we've entered
        self.e.pack()
        self.b = ttk.Button(self.top, text="Ok", command=self.cleanup)  # gets ridof the popup
        self.b.pack()
        self.value = tk.StringVar(self.top)

    def cleanup(self):
        """destroys popupWindow"""
        self.value = self.e.get()
        self.top.destroy()
