import tkinter as tk
from tkinter import ttk


class popupWindow7(object):
    def __init__(self, master, df):
        top = self.top = tk.Toplevel(master)
        self.canvas = tk.Canvas(top, bg="white")
        top.title("Data preview")
        self.canvas.pack()
        self.l = tk.Label(self.canvas, text="Data Preview")
        self.l.pack()
        cols = list(df.columns)

        tree = ttk.Treeview(self.canvas)
        tree.pack()
        tree["columns"] = cols
        for i in cols:
            tree.column(i, anchor="w")
            tree.heading(i, text=i, anchor="w")

        for index, row in df.iterrows():
            tree.insert("", 0, text=index, values=list(row))
        tree["show"] = "headings"
        self.b = tk.Button(
            top, text="Load data", command=self.cleanup1, bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6"
        )
        self.b.pack()
        self.c = tk.Button(
            top, text="Cancel", command=self.cleanup2, bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6"
        )
        self.c.pack()

    def cleanup1(self):
        self.value = "load"
        self.top.destroy()

    def cleanup2(self):
        self.value = "cancel"
        self.top.destroy()
